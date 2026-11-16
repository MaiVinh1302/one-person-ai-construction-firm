# TÀI LIỆU KỸ THUẬT & HƯỚNG DẪN PHÁT TRIỂN TIẾP: TIẾN ĐỘ CPM PRO
**Hệ thống:** TT GROUP Digital Suite — Mô-đun Quản lý & Lập Tiến độ Thi công CPM  
**Vị trí triển khai:** `/tiendo/` (Trang chính: `index.html`, Assets: `assets/`, Entrypoint alias: `tiendo_cpm.html`)  
**Truy cập Production:** [https://maivinh1302.github.io/chanh-dien-ai-pro/tiendo/](https://maivinh1302.github.io/chanh-dien-ai-pro/tiendo/)

---

## 1. TỔNG QUAN KIẾN TRÚC MÃ NGUỒN (ARCHITECTURE OVERVIEW)

Ứng dụng được xây dựng theo mô hình **Single Page Application (SPA)** chạy hoàn toàn phía Client (Client-side execution), đảm bảo tính riêng tư, bảo mật dữ liệu công trình và khả năng hoạt động Offline 100%.

```
chanh-dien-ai-pro/
├── index.html                    # Dashboard chính (Portal TT Group Digital Suite)
├── tiendo_cpm.html               # Entry redirect alias dẫn vào ./tiendo/
└── tiendo/
    ├── index.html                # Single Page App chính của Tiến độ CPM
    ├── README_TIENDO_CPM.md      # Tài liệu hướng dẫn kỹ thuật & mở rộng (File này)
    └── assets/                   # 52 bundles & modules đã chuẩn hóa đường dẫn tương đối
        ├── index-CysQ3Hvq.js     # Master Core Application Entrypoint & Main Layout
        ├── index-Db4TNw7f.css    # Tailwind CSS & UI design system
        ├── useProjectStore-LeN-VKRE.js   # Zustand State Management & Project Store
        ├── cpm-BKLu71iH.js       # CPM Engine (Forward/Backward pass, Float, Cycle detection)
        ├── schedule-CCvcjxPx.js  # WBS Schedule Engine & Date/Calendar mapping
        ├── calendar-CmDynvbO.js  # Lịch làm việc công trường & Ngày lễ Tết Việt Nam
        ├── linkParser-CQ-TLxGC.js # Parser liên kết tiền nhiệm (FS, SS, FF, SF + Lag)
        ├── baseline-BZriXUT1.js  # Baseline Store & Variance calculation
        ├── progress-CIftQ2Qi.js  # Tiến độ thực tế & S-Curve Calculation
        ├── resources-Crd6liX4.js # Cân bằng tài nguyên, nhân lực & thiết bị thi công
        ├── subcontractorPackage-CtxL5xWw.js # Cắt gói thầu phụ
        ├── SubcontractorMergeModal-BOBlSb4v.js # Hợp nhất dữ liệu thầu phụ
        ├── scheduleCompression-CBmAhW18.js # Thuật toán Nén tiến độ (Fast-track/Crash)
        ├── validate-D2St-lf2.js  # Kiểm toán chất lượng & Bẫy lỗi logic tiến độ
        ├── excelExport-BLzjI3Co.js / excelImport-Cxt7PcXY.js # Bộ xử lý Excel 2 chiều
        ├── msProjectXml-CxbOzQ8Z.js # Chuyển đổi định dạng MS Project XML
        ├── vendor-pdf-JppSO4cP.js # Kết xuất bản vẽ Gantt PDF A3/A1
        ├── vendor-exceljs-CNozmsZd.js # ExcelJS Engine
        └── vendor-react-D5gg2pXM.js # React 18 Core Runtime
```

---

## 2. ĐỘNG CƠ TÍNH TOÁN ĐƯỜNG GĂNG (CPM ENGINE MATH)

### 2.1. Cấu trúc Dữ liệu Đầu vào (Data Schema)
Một công việc (`Task`) trong hệ thống được định nghĩa với các thuộc tính cốt lõi:
```typescript
interface Task {
  id: string;               // ID duy nhất (vd: "task-1")
  code?: string;            // Mã công việc (vd: "WBS-1.1")
  name: string;             // Tên công tác thi công
  kind: 'task' | 'summary' | 'milestone'; // Công việc thường / Hạng mục mẹ / Mốc tiến độ
  durationDays: number;     // Thời lượng thi công (ngày làm việc)
  level: number;            // Cấp bậc WBS (0: Dự án, 1: Giai đoạn, 2: Hạng mục...)
  links: Link[];            // Danh sách liên kết tiền nhiệm
  progress: number;         // % hoàn thành (0 - 100)
  startDate?: string;       // Ngày bắt đầu (YYYY-MM-DD)
  endDate?: string;         // Ngày kết thúc (YYYY-MM-DD)
  constraintType?: 'ASAP' | 'MSO' | 'FNLT' | 'SNET'; // Ràng buộc ngày
  constraintDate?: string;  // Ngày áp dụng ràng buộc
  isLocked?: boolean;       // Khóa không cho thuật toán nén tiến độ
}

interface Link {
  fromId: string;           // ID công việc tiền nhiệm
  toId: string;             // ID công việc kế nhiệm
  type: 'FS' | 'SS' | 'FF' | 'SF'; // Loại quan hệ
  lag: number;              // Độ trễ (ngày, có thể âm hoặc dương)
}
```

### 2.2. Thuật toán Duyệt xuôi (Forward Pass) & Duyệt ngược (Backward Pass)
Nằm trong tệp `cpm-BKLu71iH.js`:
1. **Kiểm tra Vòng lặp (Cycle Detection):** Sử dụng thuật toán Duyệt đồ thị theo chiều sâu (DFS with recursion stack tracking). Nếu phát hiện chu trình đóng kín $A \to B \to C \to A$, hệ thống lập tức ngắt tính toán và trả về mảng `cycleIds` để thông báo lỗi cho người dùng.
2. **Forward Pass (Tính Early Start - ES & Early Finish - EF):**
   * Với liên kết `FS`: $ES_j = \max(ES_j, EF_i + lag)$
   * Với liên kết `SS`: $ES_j = \max(ES_j, ES_i + lag)$
   * Với liên kết `FF`: $EF_j = \max(EF_j, EF_i + lag)$
   * Với liên kết `SF`: $EF_j = \max(EF_j, ES_i + lag)$
   * Thời lượng: $EF = ES + durationDays - 1$ (theo ngày làm việc trên lịch công trường).
3. **Backward Pass (Tính Late Finish - LF & Late Start - LS):**
   * Lấy $LF_{\text{project}} = \max(EF_{\text{all\_tasks}})$.
   * Duyệt ngược từ các công việc kết thúc về điểm khởi đầu để tính $LF$ và $LS = LF - durationDays + 1$.
4. **Tính Dự trữ Toàn phần (Total Float - TF) & Dự trữ Tự do (Free Float - FF):**
   $$\text{Total Float} (TF) = LS - ES = LF - EF$$
   $$\text{Free Float} (FF) = \min_{k \in \text{successors}}(ES_k - \text{relationship\_offset}) - EF$$
5. **Nhận diện Đường găng (Critical Path):**
   * Mọi công việc có $TF \le 0$ được đánh dấu `isCritical = true` và tô màu đỏ trên biểu đồ Gantt.

---

## 3. CƠ CHẾ ĐẶC BIỆT CỦA ỨNG DỤNG & CÁCH TÙY BIẾN THÊM

### 3.1. Cơ chế Cắt & Hợp nhất Thầu phụ (Subcontractor Slicing & Merge)
* **Vị trí file:** `assets/subcontractorPackage-CtxL5xWw.js` và `assets/SubcontractorMergeModal-BOBlSb4v.js`.
* **Quy trình hoạt động:**
  1. Tổng thầu lọc các công việc thuộc trách nhiệm của một Nhà thầu phụ (dựa trên cột Resource hoặc tiền tố WBS).
  2. Bấm xuất gói: Hệ thống tạo ra một file `.tiendo.json` con chứa tập hợp các task được chỉ định và các mốc liên kết giao diện (Interface Milestones).
  3. Thầu phụ mở ứng dụng, nạp file con, cập nhật tiến độ (% hoàn thành, ngày thực tế bắt đầu/kết thúc).
  4. Tổng thầu mở tiến độ tổng, bấm **"Hợp nhất thầu phụ"**, chọn file của thầu phụ gửi về. Hàm merge sẽ đối chiếu `id` công việc và cập nhật đè tiến độ thực tế mà không làm thay đổi logic các công việc khác của dự án.
* **Hướng phát triển tiếp:** Bạn có thể tích hợp API gửi mail tự động hoặc webhook thông báo tới nhóm Zalo/Telegram của từng Nhà thầu phụ khi có phiên bản cập nhật.

### 3.2. Cơ chế Nén tiến độ (Schedule Compression)
* **Vị trí file:** `assets/scheduleCompression-CBmAhW18.js`.
* **Hai giải pháp nén:**
  1. *Fast-tracking (Song song hóa):* Chuyển các mối nối `FS` trên đường găng thành `SS` có độ trễ hợp lý.
  2. *Crashing (Rút ngắn thời lượng):* Giảm thời lượng các công việc găng có cản trở nhỏ nhất.
* **Đặc tính `isLocked`:** Đối với các công tác bê tông (bảo dưỡng 28 ngày, 14 ngày dỡ cốp pha), kiểm định an toàn, thí nghiệm vật liệu, kỹ sư bấm nút "Khóa". Thuật toán nén tiến độ sẽ tự động bỏ qua các công tác này, tránh tình trạng "ép tiến độ vi phạm tiêu chuẩn kỹ thuật".

### 3.3. Tương thích 2 chiều với Excel & MS Project XML
* **Clipboard Paste Engine (`assets/excelClipboard-D_IgNGVI.js`):**
  * Kỹ sư chỉ cần bôi đen bảng tiến độ trong Excel (cột Tên, Thời lượng, Bắt đầu, Tiền nhiệm) $\to$ `Ctrl+C` $\to$ Vào ứng dụng bấm `Ctrl+V`.
  * Modal `ExcelPastePreviewModal` sẽ mở ra cho phép ánh xạ cột (Mapping columns) trực quan trước khi dán vào WBS.
* **MS Project XML Converter (`assets/msProjectXml-CxbOzQ8Z.js`):**
  * Đọc thẻ `<Task>`, `<PredecessorLink>`, `<ExtendedAttribute>` từ file `.xml` xuất ra từ MS Project.
  * Xuất ra file `.xml` chuẩn Microsoft Project để nộp cho Chủ đầu tư/Tư vấn giám sát đòi hỏi hồ sơ định dạng truyền thống.

---

## 4. HƯỚNG DẪN MỞ RỘNG & TÍCH HỢP TÍNH NĂNG MỚI (DEVELOPER ROADMAP)

Để phát triển tiếp các tính năng bổ sung dựa trên nền tảng sẵn có:

### 4.1. Bổ sung Cột Chi phí & Bóc tách BOQ Giá trị Thanh toán
* Trong store `useProjectStore-LeN-VKRE.js`, bổ sung vào schema `Task`:
  ```javascript
  {
    donGia: 0,              // Đơn giá dự toán (VNĐ)
    khoiLuongKeHoach: 0,    // Khối lượng hợp đồng
    khoiLuongThucTe: 0,     // Khối lượng nghiệm thu kỳ này
    thanhTien: 0            // Giá trị lũy kế
  }
  ```
* Kết hợp với mô-đun S-Curve (`progress-CIftQ2Qi.js`) để vẽ đồng thời **Đường cong S-Curve Khối lượng** và **Đường cong S-Curve Dòng tiền (Cashflow S-Curve)**.

### 4.2. Kết nối Backend Database Đám mây (Firebase / Supabase / PostgreSQL)
* Hiện tại file `assets/firebaseClient-C_cwzIxI.js` đã tích hợp sẵn thư viện Firebase SDK.
* Để kích hoạt chia sẻ trực tuyến cho Doanh nghiệp:
  1. Tạo một project trên Firebase Console (hoặc Supabase).
  2. Cập nhật cấu hình `firebaseConfig` trong `assets/firebaseClient-C_cwzIxI.js` với API Key của đơn vị.
  3. Mọi thay đổi trên Master Gantt sẽ được lắng nghe (`onSnapshot`) và đồng bộ tức thời đến toàn bộ điện thoại di động của Ban Chỉ huy công trường.

### 4.3. Tích hợp sâu vào Hệ sinh thái TT Group Digital Suite
* **Liên kết với QLVB (`qlvb.html`):** Cho phép gắn mã văn bản đến/đi, biên bản nghiệm thu (BBNTCV) trực tiếp vào từng thanh công việc Gantt.
* **Liên kết với Foxit PDF Editor (`pdf_editor.html`):** Cho phép mở trực tiếp bản vẽ thiết kế thi công/bản vẽ hoàn công đính kèm tương ứng với đầu việc đang chọn.

---

## 5. BẢNG PHÍM TẮT THAO TÁC NHANH (QUICK SHORTCUTS)
* `Insert`: Chèn nhanh một công việc mới ngay phía dưới dòng đang chọn.
* `Ctrl + Shift + Enter`: Chèn công việc mới phía trên dòng đang chọn.
* `Ctrl + Right Arrow`: Thụt lề sang phải (Indent) $\to$ Biến công việc thành công việc con (Hạ cấp WBS).
* `Ctrl + Left Arrow`: Thụt lề sang trái (Outdent) $\to$ Nâng cấp WBS.
* `Delete`: Xóa công việc đang chọn (kèm hộp thoại xác nhận an toàn).
* `Ctrl + Z` / `Ctrl + Y`: Hoàn tác (Undo) / Làm lại (Redo) mọi thao tác.
* `F1`: Mở sổ tay Hướng dẫn sử dụng & Trung tâm trợ giúp kiến thức CPM.
