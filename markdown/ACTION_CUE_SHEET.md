# 🎬 KỊCH BẢN HÀNH ĐỘNG (ACTION CUE SHEET) - 5 PHÚT 30 GIÂY

Tài liệu này hướng dẫn chi tiết các thao tác bạn cần thực hiện trên màn hình để khớp với file âm thanh `VOICEOVER_SCRIPT_FINAL.txt`.

**Lưu ý:**

- **Chuẩn bị sẵn các tab:** Terminal, VS Code, Browser (MinIO, Superset, Jupyter), Slide/Ảnh kiến trúc.
- **Tốc độ:** Thực hiện dứt khoát, tránh rê chuột vòng vo.

---

| Thời gian (Dự kiến) | Nội dung giọng đọc (Cues)                                              | Hành động trên màn hình (Visuals)                                                                                                                                                                                                      |
| :------------------ | :--------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **0:00 - 0:45**     | "Xin chào... Data Lakehouse... On-premise trên nền tảng Docker."       | **[Slide/Ảnh]** Mở hình sơ đồ kiến trúc hệ thống (Architecture Diagram).<br>Dùng chuột khoanh vùng các cụm MinIO, Spark, ClickHouse khi giọng đọc nhắc tên công nghệ.                                                                  |
| **0:45 - 1:15**     | "Một trong những tiêu chí quan trọng... `run_full_pipeline.sh`"        | **[Terminal]** Gõ lệnh `./scripts/run_full_pipeline.sh` và ấn Enter.<br>Khi log bắt đầu chạy, **TUA NHANH VIDEO (x4)** đoạn log cài đặt Docker/Container khởi động.                                                                    |
| **1:15 - 1:45**     | "Đầu tiên là Step 0... Step 1: Ingestion... `bronze_layer.py`"         | **[Terminal]** Chỉ chuột vào dòng log màu xanh `STEP 1: BRONZE LAYER`.<br>**[VS Code]** Switch sang file `scripts/bronze_layer.py`.<br>Trỏ chuột vào đoạn code `writeTo("demo.bronze.transactions")`.                                  |
| **1:45 - 2:25**     | "Sau khi nạp xong... Silver Layer... `dbt`... Schema Evolution"        | **[VS Code]** Mở file `models/silver/silver_transactions.sql`.<br>Bôi đen hoặc chỉ vào đoạn logic `COALESCE` (xử lý Null) và các cột mới tạo.<br>**[Browser]** Mở tab **MinIO Console**, refresh để thấy folder `silver` đã xuất hiện. |
| **2:25 - 2:50**     | "Tiếp đến là Gold Layer... Aggregation... Partitioning"                | **[VS Code]** Mở file `models/gold/kpi_summary.sql`.<br>Chỉ vào các hàm `SUM`, `COUNT`.<br>Quay lại Terminal một chút để thấy log `dbt run` đã chạy xong (hiện chữ PASS màu xanh).                                                     |
| **2:50 - 3:20**     | "Dữ liệu đã sạch... Serving Layer... `serving_layer.py`... ClickHouse" | **[VS Code]** Mở file `scripts/serving_layer.py`.<br>**[Terminal]** Chỉ vào dòng log `STEP 3: SERVING LAYER`.<br>Nếu có thể, mở nhanh tab giao diện ClickHouse (nếu có) hoặc chỉ cần focus vào log insert.                             |
| **3:20 - 3:45**     | "Step 4: Auto Visualization... `setup_superset.py`"                    | **[VS Code]** Mở file `scripts/setup_superset.py`.<br>**[Terminal]** Lúc này terminal báo: `🎉 PIPELINE HOÀN TẤT`. Chỉ chuột vào thông báo này.                                                                                        |
| **3:45 - 4:45**     | "Đây là kết quả cuối cùng... Fraud Rate... Hourly Analysis..."         | **[Browser]** Chuyển sang tab **Superset Dashboard**.<br>- **Fraud Rate:** Rê chuột vào số to (Big Number).<br>- **Hourly:** Rê chuột vào cột cao nhất (lúc 2-3h sáng).<br>- Scroll xuống dưới xem các biểu đồ Product/Card.           |
| **4:45 - 5:15**     | "Trước khi kết thúc... Time Travel... Rollback"                        | **[Browser]** Chuyển sang tab **Jupyter Lab** (`05_time_travel_demo.ipynb`).<br>Cuộn xuống cell `History` hoặc cell `Rollback`.<br>Bôi đen dòng lệnh `CALL demo.system.rollback_to_snapshot`.                                          |
| **5:15 - 5:30**     | "Tổng kết lại... Cảm ơn ban giám khảo."                                | **[Slide/Ảnh]** Quay lại màn hình Architecture ban đầu hoặc Slide "Thank You".<br>Ngừng thao tác.                                                                                                                                      |

---

## 🛠 Mẹo khi quay:

1.  **Terminal:** Trước khi quay hãy gõ lệnh `clear` để màn hình sạch sẽ.
2.  **Chuột:** Tăng kích thước con trỏ chuột lên một chút để dễ nhìn trên video.
3.  **Superset:** Load sẵn Dashboard 1 lần trước khi quay để tránh bị loading lâu.
