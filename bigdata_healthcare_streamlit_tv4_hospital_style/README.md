# Big Data Healthcare — TV4 Dashboard (Hospital Style)

Dashboard Streamlit giữ nguyên bố cục/CSS hiện tại, sử dụng Gold `encounter_features` và Flask API model Linear Regression.

## Dữ liệu Gold

Mặc định dashboard đọc toàn bộ các file `part-*.parquet` tại:

```text
C:\Users\truon\OneDrive\Documents\bigdata\model\handoff\encounter_features
```

Có thể ghi đè bằng biến môi trường `GOLD_DATA_DIR`. Dataset phải có 9 cột:

```text
encounter_id, age, gender, race, ethnicity, encounter_class,
payer, condition, total_claim_cost
```

`patient_id` không thuộc Gold schema. Dashboard cache dữ liệu sau lần đọc đầu tiên và không đọc `_SUCCESS` như dữ liệu.

Chỉ dùng dữ liệu demo khi chủ động bật `ALLOW_DEMO_DATA=true`; mặc định là tắt và dashboard báo lỗi nếu không tìm thấy Gold.

## Prediction API

Mặc định API là `http://localhost:5005` (có thể ghi đè bằng `API_BASE_URL`).

```text
GET  /health
POST /predict
```

Payload `/predict`:

```json
{
  "age": 45,
  "gender": "M",
  "race": "white",
  "ethnicity": "nonhispanic",
  "encounter_class": "ambulatory",
  "payer": "Medicare",
  "condition": "Hypertension"
}
```

API phải trả `model_ready: true` ở `/health` và prediction dưới key `predicted_total_claim_cost`. Khi API lỗi hoặc offline, dashboard chỉ báo lỗi và không tạo số giả.

## Chạy

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Mở `http://localhost:8501`.
