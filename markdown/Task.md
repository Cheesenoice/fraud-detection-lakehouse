# FULLSTACK OPEN-SOURCE LAKEHOUSE PLATFORM

## PHẦN 1: GIỚI THIỆU BÀI TOÁN

Trong bối cảnh Cách mạng Công nghiệp 4.0 đang diễn ra mạnh mẽ tại Việt Nam, nhu cầu về nhân lực chất lượng cao trong lĩnh vực Khoa học Máy tính (Computer Science) và Khoa học Dữ liệu (Data Science) đã vượt xa khỏi các yêu cầu lập trình cơ bản. Các doanh nghiệp hiện đại, đặc biệt là trong lĩnh vực Thương mại điện tử (E-commerce), đang đối mặt với những thách thức phức tạp liên quan đến việc xử lý dữ liệu phi cấu trúc và xây dựng các nền tảng dữ liệu lớn (Big Data Platform) có khả năng mở rộng.

Thí sinh sẽ đóng vai trò là **Kỹ sư Dữ liệu (Data Engineer)** tại một công ty công nghệ (giả định), chịu trách nhiệm xây dựng hạ tầng dữ liệu thế hệ mới: **Data Lakehouse**.

- **Nhiệm vụ:** Thiết lập toàn bộ hệ thống từ con số 0 (from scratch) sử dụng Docker, triển khai các dịch vụ, nạp dữ liệu lớn, chuyển đổi dữ liệu và trực quan hóa.
- **Yêu cầu:** Tuyệt đối **KHÔNG** sử dụng các dịch vụ Cloud Managed (như AWS S3, Snowflake, Databricks). Bạn phải tự host các giải pháp mã nguồn mở tương đương (MinIO thay S3, Spark/Iceberg thay Databricks, ClickHouse thay Snowflake).
- **Phần cứng khuyến nghị:** RAM khuyến nghị 16GB để chạy đồng thời các container Spark và ClickHouse. Nếu sử dụng máy ảo, cần cung cấp lại cấu hình chi tiết cho BTC.

---

## PHẦN 2: CÔNG NGHỆ ÁP DỤNG

Đề xuất công nghệ cụ thể và bắt buộc, nhằm đảm bảo sinh viên tiếp cận được các chuẩn mực mới nhất của ngành:

| Tầng kiến trúc          | Công nghệ bắt buộc    |
| :---------------------- | :-------------------- |
| **Storage (Lưu trữ)**   | MinIO                 |
| **Table Format**        | Apache Iceberg        |
| **Compute (Tính toán)** | Apache Spark          |
| **Serving (Truy vấn)**  | ClickHouse            |
| **Transformation**      | dbt (data build tool) |
| **Visualization**       | Apache Superset       |

---

## PHẦN 3: DỮ LIỆU & KỊCH BẢN ỨNG DỤNG (USE CASE)

Thí sinh được tự do lựa chọn tập dữ liệu trên Kaggle về 1 trong 2 kịch bản dưới đây. Dữ liệu cần có độ phức tạp cao để phát huy sức mạnh LakeHouse.

### Lựa chọn A: E-commerce Event History (Phân tích hành vi người dùng)

- **Dữ liệu:** Bộ dữ liệu hành vi người dùng (User Behavior) từ các sàn thương mại điện tử lớn (ví dụ: REES46 dataset trên Kaggle, eCommerce Events History in Cosmetics Shop).
- **Quy mô:** Hàng triệu bản ghi (Rows).
- **Bài toán nghiệp vụ:** Phân tích phễu chuyển đổi, phân tích doanh thu theo thời gian thực, phân khúc khách hàng (RFM Analysis).
- **Thách thức kỹ thuật:** Dữ liệu sự kiện (Clickstream) có tốc độ sinh ra nhanh, cần phân vùng (Partitioning) theo ngày/giờ trong Iceberg để tối ưu truy vấn.

### Lựa chọn B: Credit Card Fraud Detection (Phát hiện gian lận tài chính)

- **Dữ liệu:** Các giao dịch thẻ tín dụng (bao gồm giao dịch gian lận và bình thường). (Ví dụ: IEEE-CIS Fraud Detection)
- **Bài toán nghiệp vụ:** Phát hiện gian lận thời gian thực, phân tích xu hướng gian lận theo vị trí địa lý hoặc loại thẻ.
- **Thách thức kỹ thuật:** Yêu cầu tính năng "Time Travel" của Iceberg để truy vấn lại trạng thái dữ liệu tại thời điểm quá khứ nhằm kiểm tra lại các giao dịch nghi vấn.

---

## PHẦN 4: QUY TRÌNH TRIỂN KHAI

Hệ thống cần được xây dựng theo kiến trúc **Medallion** qua 5 bước:

### Bước 1: Thiết lập hạ tầng

- Xây dựng `docker-compose.yml` khởi chạy toàn bộ: MinIO, Spark Master/Worker, ClickHouse Server, Superset, Iceberg REST Catalog.
- Cấu hình mạng (Docker Network) để các container giao tiếp được với nhau.

### Bước 2: Ingestion & Bronze Layer (Dữ liệu Thô)

- Sử dụng Spark để đọc dữ liệu thô (CSV/JSON) và ghi dữ liệu vào MinIO dưới định dạng Apache Iceberg (Bảng Bronze).
- Giữ nguyên dữ liệu gốc, chỉ thêm các cột metadata như `_ingestion_time`, `_source_file`.

### Bước 3: Transformation & Silver Layer (Dữ liệu Sạch)

- Sử dụng dbt kết hợp với Spark để làm sạch dữ liệu.
- Với giả lập thay đổi cấu trúc dữ liệu nguồn (ví dụ: thêm cột `payment_method` vào ngày thứ t), hệ thống Apache Iceberg phải tự động xử lý, thích ứng mà không cần viết lại toàn bộ dữ liệu.

### Bước 4: Aggregation & Gold Layer (Dữ liệu Nghiệp vụ)

- Tạo các bảng tổng hợp (Aggregated Tables) phục vụ báo cáo (ví dụ: `daily_sales_by_category`).
- Tối ưu hóa hiệu năng bằng kỹ thuật phân vùng (Partitioning) và sắp xếp dữ liệu (Z-Ordering) trong Iceberg.

### Bước 5: Serving & Visualization với ClickHouse và Superset

- **Tích hợp ClickHouse - Iceberg:** Thí sinh cần cấu hình ClickHouse Iceberg Engine (`ENGINE = IcebergS3`) để ClickHouse có thể truy vấn trực tiếp vào các file Parquet/Iceberg nằm trên MinIO mà không cần copy dữ liệu (Zero-Copy Architecture). Khuyến khích thí sinh đề xuất phương án xử lý khác (Ví dụ sử dụng spark để copy gold từ MinIO/Iceberg sang Clickhouse).
- **Kết nối Superset:** Cài đặt driver `clickhouse-connect` cho Superset.
- **Xây dựng Dashboard:** Tạo ít nhất 3 biểu đồ tương tác thể hiện các chỉ số nghiệp vụ quan trọng (KPIs) từ dữ liệu Gold Layer.

---

## PHẦN 5: TIÊU CHÍ ĐÁNH GIÁ

| Hạng mục                            | Tiêu chí chi tiết                                                                                                                          |
| :---------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------- |
| **Hạ tầng & DevOps**                | Khả năng triển khai tự động bằng Docker Compose. Hệ thống chạy ổn định, không lỗi kết nối.                                                 |
| **Kiến trúc dữ liệu**               | Tuân thủ mô hình Medallion. Thiết kế Partitioning hợp lý cho Iceberg.                                                                      |
| **Kỹ thuật xử lý (Spark/dbt)**      | Code Spark tối ưu, logic dbt rõ ràng (có test, document). Xử lý thành công Schema Evolution.                                               |
| **Hiệu năng truy vấn (ClickHouse)** | Tốc độ truy vấn trên ClickHouse nhanh (độ trễ thấp). Sử dụng đúng các kỹ thuật tối ưu của ClickHouse (Primary Key, Data Skipping Indices). |
| **Trực quan hóa (Superset)**        | Dashboard có ý nghĩa nghiệp vụ giao diện thân thiện, dữ liệu chính xác.                                                                    |

---

## PHẦN 6: YÊU CẦU NỘP BÀI

- Bản mềm các tài liệu: báo cáo (cần giới thiệu bài toán, tóm tắt và phân tích bài toán được giao) tối đa 20 trang, slide thuyết trình.
- Các tệp mã nguồn dự án (Jupyter Notebook / Python Script) chứa toàn bộ quá trình phân tích, xử lý dữ liệu và huấn luyện mô hình, `README.md`, script hướng dẫn chạy code (bắt buộc).
- Các notebook trên mạng (ví dụ: Kaggle notebook, Google Collab,...) các đội thi cần tải xuống và đồng thời gắn thêm link trực tiếp vào trong mã nguồn để nộp.
- Link Github (nếu có) được gắn vào báo cáo, cần đảm bảo quyền truy cập vào các đường link này. Sau thời gian nộp bài, không được có bất kỳ commit nào lên Github.
- Video demo hệ thống (3 - 5 phút).
- Thời gian báo cáo: 20 phút, trong đó có 5 phút demo sản phẩm, 10 phút thuyết trình và 5 phút vấn đáp với ban giám khảo.

**LƯU Ý:**

- Đội thi nộp bản mềm dưới định dạng file **pdf** hoặc **pptx**, không nộp dưới dạng ảnh, ảnh scan từ báo cáo bản cứng. Bản nộp cần là nộp bản gốc cho BTC trước thời gian quy định.
- **Ngôn ngữ sử dụng:** Sử dụng ngôn ngữ tiếng Việt, một số thuật ngữ chuyên ngành khó dịch có thể sử dụng tiếng Anh nhưng cần có chú thích trong phụ lục. Các từ ngữ không sử dụng từ địa phương, không sử dụng teencode. Các từ ngữ viết tắt cần được chú thích rõ ràng trong phụ lục.

---

## PHẦN 7: TÀI LIỆU THAM KHẢO

1.  **MinIO (2023)** _Building a Data Lakehouse using Apache Iceberg and MinIO_. MinIO Blog. Truy cập tại: [https://blog.min.io/building-a-data-lakehouse-using-apache-iceberg-and-minio/](https://blog.min.io/building-a-data-lakehouse-using-apache-iceberg-and-minio/)
2.  **CodeWithYu (2025)** _End to End Modern Distributed Data Lakehouse using Apache Iceberg, Trino, Airflow, DBT and Minio_. YouTube, 27 September 2025. Truy cập tại: [https://www.youtube.com/watch?v=GGdVfDdeNYs](https://www.youtube.com/watch?v=GGdVfDdeNYs)
