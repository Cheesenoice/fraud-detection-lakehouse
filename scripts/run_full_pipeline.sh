#!/bin/bash

###############################################################################
# FULL LAKEHOUSE PIPELINE AUTOMATION - ONE COMMAND
# Credit Card Fraud Detection - IEEE-CIS Dataset
# Chỉ cần 1 lệnh: ./run_full_pipeline.sh
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║         🚀 FULL LAKEHOUSE PIPELINE - ONE COMMAND                     ║"
echo "║         Credit Card Fraud Detection - IEEE-CIS Dataset               ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

###############################################################################
# STEP 0: Docker Compose Up
###############################################################################
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🐳 STEP 0: Khởi động Docker Stack${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker không chạy. Vui lòng khởi động Docker trước.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker daemon đang chạy${NC}"

# Start containers
cd "$PROJECT_DIR"
echo "   🔄 Đang khởi động containers..."
docker compose up -d

# Wait for containers to be ready
echo "   ⏳ Đợi containers khởi động..."
REQUIRED_CONTAINERS=("spark-iceberg" "clickhouse" "dbt" "superset" "minio" "iceberg-rest")
MAX_WAIT=120
WAIT_TIME=0

while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    ALL_RUNNING=true
    for container in "${REQUIRED_CONTAINERS[@]}"; do
        if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
            ALL_RUNNING=false
            break
        fi
    done
    
    if $ALL_RUNNING; then
        break
    fi
    
    sleep 5
    WAIT_TIME=$((WAIT_TIME + 5))
    echo -n "."
done

if [ $WAIT_TIME -ge $MAX_WAIT ]; then
    echo -e "\n${RED}❌ Timeout: Containers không khởi động kịp${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Tất cả containers đang chạy${NC}"

# Start Thrift Server for dbt
echo "   🔄 Khởi động Spark Thrift Server..."

# Stop any existing Thrift Server first
docker exec spark-iceberg /opt/spark/sbin/stop-thriftserver.sh 2>/dev/null || true
sleep 3

# Start Thrift Server with proper config (full Iceberg + S3 settings)
docker exec -d spark-iceberg /opt/spark/sbin/start-thriftserver.sh \
    --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
    --conf spark.sql.catalog.demo=org.apache.iceberg.spark.SparkCatalog \
    --conf spark.sql.catalog.demo.type=rest \
    --conf spark.sql.catalog.demo.uri=http://iceberg-rest:8181 \
    --conf spark.sql.catalog.demo.io-impl=org.apache.iceberg.aws.s3.S3FileIO \
    --conf spark.sql.catalog.demo.warehouse=s3://warehouse/ \
    --conf spark.sql.catalog.demo.s3.endpoint=http://minio:9000 \
    --conf spark.sql.catalog.demo.s3.path-style-access=true \
    --conf spark.sql.catalog.demo.s3.access-key-id=admin \
    --conf spark.sql.catalog.demo.s3.secret-access-key=password123 \
    --conf spark.hadoop.fs.s3a.endpoint=http://minio:9000 \
    --conf spark.hadoop.fs.s3a.access.key=admin \
    --conf spark.hadoop.fs.s3a.secret.key=password123 \
    --conf spark.hadoop.fs.s3a.path.style.access=true \
    --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
    --conf spark.sql.defaultCatalog=demo \
    --hiveconf hive.server2.thrift.port=10000

# Wait for Thrift Server to be ready (check port 10000)
echo "   ⏳ Đợi Thrift Server sẵn sàng (tối đa 90 giây)..."
THRIFT_WAIT=0
THRIFT_MAX=90
while [ $THRIFT_WAIT -lt $THRIFT_MAX ]; do
    # Check if port 10000 is open using Python
    if docker exec dbt python3 -c "import socket; s=socket.socket(); s.settimeout(2); exit(0 if s.connect_ex(('spark-iceberg', 10000))==0 else 1)" 2>/dev/null; then
        echo -e "\n${GREEN}✅ Thrift Server đã sẵn sàng trên port 10000${NC}"
        break
    fi
    sleep 5
    THRIFT_WAIT=$((THRIFT_WAIT + 5))
    echo -n "."
done

if [ $THRIFT_WAIT -ge $THRIFT_MAX ]; then
    echo -e "\n${RED}❌ Timeout: Thrift Server không khởi động được${NC}"
    echo "   Xem log: docker exec spark-iceberg tail -50 /opt/spark/logs/*HiveThriftServer2*.out"
    exit 1
fi

# Check data files
if [ ! -f "$PROJECT_DIR/notebooks/data/train_transaction.csv" ]; then
    echo -e "${RED}❌ Không tìm thấy train_transaction.csv${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Data files sẵn sàng${NC}"

###############################################################################
# STEP 1: Bronze Layer
###############################################################################
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📥 STEP 1: Bronze Layer - Ingest CSV vào Iceberg${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Create namespaces if they don't exist (required for first run)
echo "   🔄 Tạo namespaces trong Iceberg catalog..."
docker cp "$SCRIPT_DIR/create_namespaces.py" spark-iceberg:/tmp/create_namespaces.py
docker exec spark-iceberg /opt/spark/bin/spark-submit --master local[*] \
    --conf spark.sql.catalog.demo=org.apache.iceberg.spark.SparkCatalog \
    --conf spark.sql.catalog.demo.type=rest \
    --conf spark.sql.catalog.demo.uri=http://iceberg-rest:8181 \
    --conf spark.sql.defaultCatalog=demo \
    /tmp/create_namespaces.py 2>&1 | grep -E "(✅|⚠️|📋|Done)" || true
echo -e "   ${GREEN}✅ Namespaces đã sẵn sàng${NC}"

# Copy Bronze script to container
docker cp "$SCRIPT_DIR/bronze_layer.py" spark-iceberg:/tmp/bronze_layer.py

echo "   🔄 Đang chạy Bronze Layer ingestion..."
docker exec spark-iceberg /opt/spark/bin/spark-submit --master local[*] /tmp/bronze_layer.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Bronze Layer hoàn tất!${NC}"
else
    echo -e "${RED}❌ Bronze Layer thất bại!${NC}"
    exit 1
fi

###############################################################################
# STEP 2: dbt run
###############################################################################
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔧 STEP 2: dbt run - Tạo Silver & Gold Layers${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo "   🔄 Đang chạy dbt run..."
docker exec dbt dbt run --project-dir /usr/app

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ dbt run hoàn tất! (Silver + Gold layers)${NC}"
else
    echo -e "${RED}❌ dbt run thất bại!${NC}"
    exit 1
fi

###############################################################################
# STEP 3: Serving Layer
###############################################################################
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📤 STEP 3: Serving Layer - Copy Gold sang ClickHouse${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Copy Serving script to container
docker cp "$SCRIPT_DIR/serving_layer.py" spark-iceberg:/tmp/serving_layer.py

echo "   🔄 Đang chạy Serving Layer..."
docker exec spark-iceberg /opt/spark/bin/spark-submit --master local[*] /tmp/serving_layer.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Serving Layer hoàn tất!${NC}"
else
    echo -e "${RED}❌ Serving Layer thất bại!${NC}"
    exit 1
fi

###############################################################################
# STEP 4: Superset Auto Setup
###############################################################################
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 STEP 4: Superset - Tự động tạo Dashboard${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo "   🔄 Đợi Superset khởi động hoàn tất..."
sleep 10

# Check and install clickhouse-connect driver if needed
echo "   🔍 Kiểm tra ClickHouse driver trong Superset..."
if docker exec superset python3 -c "import clickhouse_connect" 2>/dev/null; then
    echo -e "   ${GREEN}✅ clickhouse-connect driver đã có sẵn${NC}"
else
    echo "   📦 Đang cài đặt clickhouse-connect driver..."
    docker exec -u root superset bash -c "apt-get update -qq && apt-get install -y -qq curl > /dev/null 2>&1 && curl -sS https://bootstrap.pypa.io/get-pip.py | python > /dev/null 2>&1 && pip install clickhouse-connect > /dev/null 2>&1" 2>/dev/null
    
    if docker exec superset python3 -c "import clickhouse_connect" 2>/dev/null; then
        echo -e "   ${GREEN}✅ clickhouse-connect driver đã cài đặt thành công${NC}"
        echo "   🔄 Đang restart Superset để load driver..."
        docker restart superset > /dev/null 2>&1
        
        # Wait for Superset to be ready after restart
        echo "   ⏳ Đợi Superset khởi động lại (60 giây)..."
        SUPERSET_WAIT=0
        SUPERSET_MAX=90
        while [ $SUPERSET_WAIT -lt $SUPERSET_MAX ]; do
            if curl -s "http://localhost:8088/health" 2>/dev/null | grep -q "OK"; then
                echo -e "\n   ${GREEN}✅ Superset đã sẵn sàng${NC}"
                break
            fi
            sleep 5
            SUPERSET_WAIT=$((SUPERSET_WAIT + 5))
            echo -n "."
        done
        
        if [ $SUPERSET_WAIT -ge $SUPERSET_MAX ]; then
            echo -e "\n   ${YELLOW}⚠️  Superset chưa sẵn sàng, tiếp tục...${NC}"
        fi
    else
        echo -e "   ${YELLOW}⚠️  Không thể cài clickhouse-connect driver${NC}"
    fi
fi

# Run Superset setup script
echo "   🔄 Đang setup Superset (Database, Datasets, Charts, Dashboard)..."
python3 "$SCRIPT_DIR/setup_superset.py"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Superset setup hoàn tất!${NC}"
else
    echo -e "${YELLOW}⚠️  Superset auto-setup có lỗi. Bạn có thể setup thủ công:${NC}"
    echo -e "${CYAN}
📌 Để tạo Dashboard trong Superset thủ công:
1. Mở browser: http://localhost:8088
2. Đăng nhập: admin / admin
3. Settings → Database Connections → + Database
4. Chọn 'ClickHouse Connect'
5. Connection string:
   clickhousedb://default:clickhouse123@clickhouse:8123/fraud_detection
6. Test Connection → Connect
7. Vào SQL Lab để query hoặc tạo Charts

📖 Xem hướng dẫn chi tiết: ${PROJECT_DIR}/markdown/SUPERSET_CHARTS_GUIDE.md
${NC}"
fi

###############################################################################
# FINAL SUMMARY
###############################################################################
echo -e "\n${GREEN}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    🎉 PIPELINE HOÀN TẤT!                             ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}📊 KẾT QUẢ:${NC}"
echo "   ✅ Bronze Layer: Raw CSV → Iceberg tables (demo.bronze.*)"
echo "   ✅ Silver Layer: Cleaned data (demo.silver.*)"
echo "   ✅ Gold Layer: Analytics tables (demo.gold.*)"
echo "   ✅ Serving Layer: ClickHouse tables (fraud_detection.*)"

echo -e "\n${CYAN}🌐 TRUY CẬP:${NC}"
echo "   📊 Superset Dashboard: http://localhost:8088 (admin/admin)"
echo "   📁 MinIO Console:     http://localhost:9001 (admin/password123)"
echo "   💻 Jupyter:           http://localhost:8888"
echo "   🗄️  ClickHouse:        http://localhost:8123"

echo -e "\n${YELLOW}⏱️  Hoàn tất: $(date)${NC}"
echo ""
