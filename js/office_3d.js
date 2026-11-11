// =============================================================================
// OFFICE 3D VIRTUAL FLOOR ENGINE - THREE.JS
// Sàn làm việc 3D Doanh Nghiệp Xây Dựng 1 Người (T&T AI Construction Enterprise)
// - 5 Phòng Ban Chuyên Môn + Văn Phòng Founder + Phòng Họp Hội Đồng Lớn
// - 11 Nhân Sự 3D có thể di chuyển, tuần tra, họp và quay về bàn làm việc
// - Bàn ghế công thái học, máy tính kép, kệ tài liệu pháp lý & biểu mẫu, cây xanh
// =============================================================================

class Office3DFloorEngine {
  constructor(canvasContainerId) {
    this.container = document.getElementById(canvasContainerId);
    if (!this.container) return;

    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.clock = new THREE.Clock();

    this.staffMembers = [];
    this.selectableObjects = [];
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();

    this.selectedStaff = null;
    this.targetMovePoint = null;
    this.isMeetingMode = false;
    this.isNightMode = false;

    // Định nghĩa vị trí các khu vực trọng điểm trên sàn văn phòng (Floor Plan Coordinates)
    this.ZONES = {
      FOUNDER: { name: "Văn Phòng Founder & CEO Mai Quang Vinh", center: { x: -22, z: -15 }, color: 0xf59e0b },
      BOARDROOM: { name: "Phòng Họp Lớn & Hội Đồng Xét Thầu", center: { x: 20, z: -15 }, color: 0x38bdf8 },
      LEGAL: { name: "Phòng Pháp Chế & Đàm Phán Hợp Đồng", center: { x: -22, z: 12 }, color: 0xa855f7 },
      BIDDING: { name: "Phòng Quản Lý Đấu Thầu & Mua Sắm", center: { x: -8, z: 12 }, color: 0x3b82f6 },
      QS: { name: "Phòng Kỹ Sư Dự Toán QS & BOQ", center: { x: 6, z: 12 }, color: 0x10b981 },
      QAQC: { name: "Phòng Quản Lý Chất Lượng QA/QC", center: { x: 20, z: 12 }, color: 0xf97316 },
      SETTLEMENT: { name: "Phòng Kiểm Toán Thanh & Quyết Toán", center: { x: -8, z: -15 }, color: 0xec4899 },
      MARKETING: { name: "Ban Marketing & Truyền Thông Studio", center: { x: 6, z: -15 }, color: 0xd946ef },
      RECREATION: { name: "Phòng Giải Trí & Thể Dục Wellness", center: { x: -22, z: -1 }, color: 0x10b981 },
      CANTEEN: { name: "Căn Tin & Quầy Bar Doanh Nghiệp", center: { x: 20, z: -1 }, color: 0xf59e0b },
      LOUNGE: { name: "Sảnh Lễ Tân & Tiếp Khách Trung Tâm", center: { x: 0, z: -2 }, color: 0x64748b }
    };

    // Danh sách 11 nhân sự AI kèm tọa độ bàn làm việc cá nhân (Desk Coordinates)
    this.STAFF_DATA = [
      {
        id: "founder",
        name: "Mai Quang Vinh",
        role: "Founder / CEO (Chủ tịch điều hành tối cao)",
        level: "Level 5",
        dept: "FOUNDER",
        color: 0x1e3a8a, // Navy VIP
        deskPos: { x: -22, z: -16, rot: 0 },
        meetPos: { x: 16, z: -15, rot: Math.PI / 2 }
      },
      // 1. Pháp chế
      {
        id: "legal_specialist",
        name: "Nguyễn Văn Pháp",
        role: "Chuyên viên Soạn thảo & Rà soát Hợp đồng",
        level: "Level 2",
        dept: "LEGAL",
        color: 0x9333ea,
        deskPos: { x: -24, z: 13, rot: 0 },
        meetPos: { x: 18, z: -17, rot: Math.PI }
      },
      {
        id: "legal_head",
        name: "Trần Thị Tuân Thủ",
        role: "Trưởng phòng Pháp chế & Quản trị Rủi ro",
        level: "Level 3",
        dept: "LEGAL",
        color: 0x7e22ce,
        deskPos: { x: -20, z: 13, rot: 0 },
        meetPos: { x: 18, z: -13, rot: 0 }
      },
      // 2. Đấu thầu
      {
        id: "bidding_specialist",
        name: "Lê Quang Thầu",
        role: "Chuyên viên Thẩm tra Hồ sơ Đấu thầu & Giá Mua sắm",
        level: "Level 2",
        dept: "BIDDING",
        color: 0x2563eb,
        deskPos: { x: -10, z: 13, rot: 0 },
        meetPos: { x: 20, z: -17, rot: Math.PI }
      },
      {
        id: "bidding_head",
        name: "Phạm Minh Đấu",
        role: "Trưởng phòng Quản lý Đấu thầu & Hợp đồng Mua sắm",
        level: "Level 3",
        dept: "BIDDING",
        color: 0x1d4ed8,
        deskPos: { x: -6, z: 13, rot: 0 },
        meetPos: { x: 20, z: -13, rot: 0 }
      },
      // 3. Dự toán QS
      {
        id: "qs_specialist",
        name: "Đỗ Văn Lượng",
        role: "Kỹ sư QS Bóc tách Khối lượng & Áp Định mức",
        level: "Level 2",
        dept: "QS",
        color: 0x059669,
        deskPos: { x: 4, z: 13, rot: 0 },
        meetPos: { x: 22, z: -17, rot: Math.PI }
      },
      {
        id: "qs_head",
        name: "Vũ Đình Toàn",
        role: "Trưởng phòng Thẩm tra Dự toán & Kiểm soát Chi phí",
        level: "Level 3",
        dept: "QS",
        color: 0x047857,
        deskPos: { x: 8, z: 13, rot: 0 },
        meetPos: { x: 22, z: -13, rot: 0 }
      },
      // 4. QA/QC
      {
        id: "qaqc_specialist",
        name: "Bùi Văn Nghiệm",
        role: "Kỹ sư QA/QC Giám sát Hiện trường & Hồ sơ Nghiệm thu",
        level: "Level 2",
        dept: "QAQC",
        color: 0xea580c,
        deskPos: { x: 18, z: 13, rot: 0 },
        meetPos: { x: 24, z: -17, rot: Math.PI }
      },
      {
        id: "qaqc_head",
        name: "Hoàng Văn Chuẩn",
        role: "Trưởng phòng Quản lý Chất lượng & An toàn Công trình",
        level: "Level 3",
        dept: "QAQC",
        color: 0xc2410c,
        deskPos: { x: 22, z: 13, rot: 0 },
        meetPos: { x: 24, z: -13, rot: 0 }
      },
      // 5. Quyết toán
      {
        id: "settlement_specialist",
        name: "Ngô Thị Quyết",
        role: "Chuyên viên Thẩm tra Hồ sơ Thanh Quyết toán Mẫu 08a",
        level: "Level 2",
        dept: "SETTLEMENT",
        color: 0xdb2777,
        deskPos: { x: -10, z: -15, rot: 0 },
        meetPos: { x: 26, z: -17, rot: Math.PI }
      },
      {
        id: "settlement_head",
        name: "Đặng Đức Toán",
        role: "Trưởng phòng Kiểm toán Quyết toán & Kiểm soát Ngân quỹ",
        level: "Level 3",
        dept: "SETTLEMENT",
        color: 0xbe185d,
        deskPos: { x: -6, z: -15, rot: 0 },
        meetPos: { x: 26, z: -13, rot: 0 }
      },
      // 6. Ban Marketing & Truyền thông
      {
        id: "marketing_content",
        name: "Trần Thị Lan Tỏa",
        role: "Chuyên viên Sáng tạo Nội dung & Truyền thông Xã hội",
        level: "Level 2",
        dept: "MARKETING",
        color: 0xe879f9,
        deskPos: { x: 3, z: -15, rot: 0 },
        meetPos: { x: 28, z: -17, rot: Math.PI }
      },
      {
        id: "marketing_video",
        name: "Nguyễn Huy Dựng",
        role: "Chuyên viên Thiết kế Đồ họa & Sản xuất Video Đa Phương Tiện",
        level: "Level 2",
        dept: "MARKETING",
        color: 0xc026d3,
        deskPos: { x: 7, z: -15, rot: 0 },
        meetPos: { x: 28, z: -13, rot: 0 }
      },
      {
        id: "marketing_head",
        name: "Lê Mai Truyền",
        role: "Trưởng ban Marketing & Truyền thông Thương hiệu",
        level: "Level 3",
        dept: "MARKETING",
        color: 0xa21caf,
        deskPos: { x: 9, z: -12, rot: Math.PI / 4 },
        meetPos: { x: 26, z: -15, rot: Math.PI / 2 }
      },
      // 7. Nhân sự Căn Tin & Dịch Vụ Văn Phòng
      {
        id: "canteen_barista",
        name: "Nguyễn Thị Trà My",
        role: "Barista & Chăm Sóc Quầy Bar Căn Tin",
        level: "Level 2",
        dept: "CANTEEN",
        color: 0x14b8a6, // Teal
        deskPos: { x: 18.5, z: -2.8, rot: 0 },
        meetPos: { x: 28, z: -15, rot: 0 }
      },
      {
        id: "canteen_chef",
        name: "Trần Văn Bếp",
        role: "Bếp Trưởng & Dinh Dưỡng Năng Lượng Doanh Nghiệp",
        level: "Level 2",
        dept: "CANTEEN",
        color: 0xf97316, // Orange
        deskPos: { x: 21.5, z: -2.8, rot: 0 },
        meetPos: { x: 28, z: -13, rot: 0 }
      }
    ];

    this.init();
  }

  init() {
    const width = this.container.clientWidth || 1000;
    const height = this.container.clientHeight || 650;

    // 1. Tạo Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0a0f1d);
    this.scene.fog = new THREE.FogExp2(0x0a0f1d, 0.012);

    // 2. Tạo Camera
    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.5, 300);
    this.camera.position.set(0, 38, 48);

    // 3. Tạo Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.container.appendChild(this.renderer.domElement);

    // 4. Tạo OrbitControls
    if (typeof THREE.OrbitControls !== "undefined") {
      this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;
      this.controls.maxPolarAngle = Math.PI / 2.1;
      this.controls.minDistance = 5;
      this.controls.maxDistance = 110;
      this.controls.target.set(0, 0, 0);
    }

    // 5. Thiết lập ánh sáng (Lighting)
    this.setupLighting();

    // 6. Xây dựng cấu trúc kiến trúc sàn văn phòng (Architecture)
    this.buildOfficeArchitecture();

    // 7. Bố trí nội thất từng phòng ban (Furniture, Desks, Bookshelves, Boardroom)
    this.buildAllFurniture();

    // 8. Tạo 11 Nhân sự AI 3D (Humanoid Avatars)
    this.spawnStaffAvatars();

    // 9. Lắng nghe sự kiện (Events)
    window.addEventListener("resize", () => this.onWindowResize());
    this.renderer.domElement.addEventListener("click", (e) => this.onPointerClick(e));

    // Bắt đầu Render Loop
    this.animate();
  }

  setupLighting() {
    // Ambient light dịu nhẹ
    this.ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    this.scene.add(this.ambientLight);

    // Ánh sáng mặt trời ban ngày chiếu xiên qua cửa kính
    this.sunLight = new THREE.DirectionalLight(0xfef08a, 1.1);
    this.sunLight.position.set(30, 45, 25);
    this.sunLight.castShadow = true;
    this.sunLight.shadow.mapSize.width = 2048;
    this.sunLight.shadow.mapSize.height = 2048;
    this.sunLight.shadow.camera.near = 0.5;
    this.sunLight.shadow.camera.far = 150;
    const d = 35;
    this.sunLight.shadow.camera.left = -d;
    this.sunLight.shadow.camera.right = d;
    this.sunLight.shadow.camera.top = d;
    this.sunLight.shadow.camera.bottom = -d;
    this.scene.add(this.sunLight);

    // Đèn LED trần trung tâm khu vực
    const spotLounge = new THREE.PointLight(0x38bdf8, 1.2, 35);
    spotLounge.position.set(0, 10, -2);
    this.scene.add(spotLounge);

    const spotFounder = new THREE.PointLight(0xf59e0b, 1.2, 28);
    spotFounder.position.set(-22, 9, -15);
    this.scene.add(spotFounder);

    const spotMeeting = new THREE.PointLight(0x60a5fa, 1.4, 30);
    spotMeeting.position.set(20, 9, -15);
    this.scene.add(spotMeeting);
  }

  buildOfficeArchitecture() {
    // 1. Sàn chính văn phòng (Floor Tiles: 65m x 48m)
    const floorGeo = new THREE.PlaneGeometry(65, 48);
    const floorMat = new THREE.MeshStandardMaterial({
      color: 0x111827,
      roughness: 0.25,
      metalness: 0.15
    });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    this.scene.add(floor);

    // Kẻ lưới gạch men phản chiếu nhẹ
    const grid = new THREE.GridHelper(65, 32, 0x334155, 0x1e293b);
    grid.position.y = 0.02;
    this.scene.add(grid);

    // 2. Tường bao kính xung quanh (Glass Windows)
    const glassMat = new THREE.MeshPhysicalMaterial({
      color: 0x93c5fd,
      transparent: true,
      opacity: 0.22,
      roughness: 0.1,
      transmission: 0.85,
      thickness: 0.5
    });

    const wallHeight = 5.5;
    // Tường sau (Back Wall)
    const backWall = new THREE.Mesh(new THREE.BoxGeometry(65, wallHeight, 0.4), glassMat);
    backWall.position.set(0, wallHeight / 2, -24);
    this.scene.add(backWall);

    // Tường trái & phải
    const leftWall = new THREE.Mesh(new THREE.BoxGeometry(0.4, wallHeight, 48), glassMat);
    leftWall.position.set(-32.5, wallHeight / 2, 0);
    this.scene.add(leftWall);

    const rightWall = new THREE.Mesh(new THREE.BoxGeometry(0.4, wallHeight, 48), glassMat);
    rightWall.position.set(32.5, wallHeight / 2, 0);
    this.scene.add(rightWall);

    // Khung kim loại viền sàn
    const borderMat = new THREE.MeshStandardMaterial({ color: 0x3b82f6, metalness: 0.8, roughness: 0.2 });
    const bTop = new THREE.Mesh(new THREE.BoxGeometry(65.5, 0.5, 0.5), borderMat);
    bTop.position.set(0, wallHeight, -24);
    this.scene.add(bTop);

    // 3. Vách ngăn kính giữa các phòng ban chuyên môn
    this.buildZoneDivider(-15, 12, 10, "Vách Ban Pháp Chế & Đấu Thầu");
    this.buildZoneDivider(-1, 12, 10, "Vách Ban Đấu Thầu & Dự Toán");
    this.buildZoneDivider(13, 12, 10, "Vách Ban Dự Toán & QAQC");

    // Vách kính phòng Founder
    this.buildGlassRoom(-22, -15, 14, 12, "VĂN PHÒNG FOUNDER & CEO MAI QUANG VINH");

    // Vách kính phòng Họp Hội Đồng
    this.buildGlassRoom(20, -15, 16, 12, "PHÒNG HỌP HỘI ĐỒNG LÃNH ĐẠO T&T");

    // Vách kính Phòng Giải Trí & Thể Dục Wellness
    this.buildGlassRoom(-22, -1, 14, 9, "PHÒNG GIẢI TRÍ & CHĂM SÓC SỨC KHỎE");

    // Vách kính Căn Tin & Quầy Bar Doanh Nghiệp
    this.buildGlassRoom(20, -1, 16, 9, "CĂN TIN & QUẦY BAR DOANH NGHIỆP");

    // Biển hiệu LED phát sáng cho các phòng ban
    this.createGlowSignboard("👑 PHÒNG TỔNG GIÁM ĐỐC / FOUNDER", -22, 4.8, -20.8, 0xf59e0b);
    this.createGlowSignboard("🏛️ PHÒNG HỌP HỘI ĐỒNG CHIẾN LƯỢC", 20, 4.8, -20.8, 0x38bdf8);
    this.createGlowSignboard("⚖️ BAN PHÁP CHẾ & HỢP ĐỒNG", -22, 3.8, 6.5, 0xa855f7);
    this.createGlowSignboard("📋 BAN ĐẤU THẦU & MUA SẮM", -8, 3.8, 6.5, 0x3b82f6);
    this.createGlowSignboard("📐 BAN DỰ TOÁN QS & BOQ", 6, 3.8, 6.5, 0x10b981);
    this.createGlowSignboard("🏗️ BAN CHẤT LƯỢNG QA/QC", 20, 3.8, 6.5, 0xf97316);
    this.createGlowSignboard("💰 BAN KIỂM TOÁN QUYẾT TOÁN", -8, 4.8, -20.8, 0xec4899);
    this.createGlowSignboard("🎬 BAN MARKETING & TRUYỀN THÔNG", 6, 4.8, -20.8, 0xd946ef);
    this.createGlowSignboard("🎮 PHÒNG GIẢI TRÍ & WELLNESS", -22, 4.2, 3.6, 0x10b981);
    this.createGlowSignboard("☕ CĂN TIN & QUẦY BAR DOANH NGHIỆP", 20, 4.2, 3.6, 0xf59e0b);
  }

  buildZoneDivider(x, z, length, label) {
    const dividerGeo = new THREE.BoxGeometry(0.2, 2.8, length);
    const dividerMat = new THREE.MeshPhysicalMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.35,
      roughness: 0.1
    });
    const div = new THREE.Mesh(dividerGeo, dividerMat);
    div.position.set(x, 1.4, z);
    div.castShadow = true;
    this.scene.add(div);

    // Chân đế kim loại
    const base = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.15, length), new THREE.MeshStandardMaterial({ color: 0x475569 }));
    base.position.set(x, 0.08, z);
    this.scene.add(base);
  }

  buildGlassRoom(cx, cz, w, d, title) {
    const wallH = 4.2;
    const roomMat = new THREE.MeshPhysicalMaterial({
      color: 0x0284c7,
      transparent: true,
      opacity: 0.28,
      roughness: 0.1,
      metalness: 0.1
    });

    // Mặt trước (có khoảng mở cửa)
    const front1 = new THREE.Mesh(new THREE.BoxGeometry((w - 3) / 2, wallH, 0.2), roomMat);
    front1.position.set(cx - (w / 4 + 0.75), wallH / 2, cz + d / 2);
    this.scene.add(front1);

    const front2 = new THREE.Mesh(new THREE.BoxGeometry((w - 3) / 2, wallH, 0.2), roomMat);
    front2.position.set(cx + (w / 4 + 0.75), wallH / 2, cz + d / 2);
    this.scene.add(front2);

    // Tường vách hông
    const sideWall = new THREE.Mesh(new THREE.BoxGeometry(0.2, wallH, d), roomMat);
    sideWall.position.set(cx + (cx < 0 ? w / 2 : -w / 2), wallH / 2, cz);
    this.scene.add(sideWall);
  }

  createGlowSignboard(text, x, y, z, glowColor = 0x38bdf8) {
    // Bảng hiệu 3D phát sáng
    const canvas = document.createElement("canvas");
    canvas.width = 512;
    canvas.height = 128;
    const ctx = canvas.getContext("2d");

    ctx.fillStyle = "rgba(10, 15, 30, 0.85)";
    ctx.roundRect(4, 4, 504, 120, 16);
    ctx.fill();

    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 6;
    ctx.roundRect(4, 4, 504, 120, 16);
    ctx.stroke();

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 26px Arial, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, 256, 64);

    const texture = new THREE.CanvasTexture(canvas);
    const signMat = new THREE.MeshBasicMaterial({ map: texture, transparent: true, side: THREE.DoubleSide });
    const signMesh = new THREE.Mesh(new THREE.PlaneGeometry(6.5, 1.6), signMat);
    signMesh.position.set(x, y, z);
    this.scene.add(signMesh);
  }

  buildAllFurniture() {
    // 1. Phòng Founder Mai Quang Vinh: Bàn Giám Đốc chữ L VIP
    this.createExecutiveDesk(-22, -16);
    this.createBookshelf(-27, -19, 0, "KỆ HỒ SƠ CHIẾN LƯỢC TẬP ĐOÀN T&T");
    this.createPlant(-16, -11);
    this.createExecutiveSofa(-18, -13);

    // 2. Phòng Họp Hội Đồng Lớn (Boardroom)
    this.createMeetingRoom(20, -15);

    // 3. Phòng Ban 1: Pháp chế
    this.createWorkstation(-24, 13, "Nguyễn Văn Pháp", "Hợp đồng NĐ 210");
    this.createWorkstation(-20, 13, "Trần Thị Tuân Thủ", "Kiểm duyệt QĐ 690");
    this.createBookshelf(-26.5, 13, Math.PI / 2, "KỆ LUẬT XÂY DỰNG 2026 & MẪU HĐ");

    // 4. Phòng Ban 2: Đấu thầu
    this.createWorkstation(-10, 13, "Lê Quang Thầu", "HSMT QĐ 458");
    this.createWorkstation(-6, 13, "Phạm Minh Đấu", "Đấu thầu NĐ 349");
    this.createBookshelf(-13.5, 13, Math.PI / 2, "KỆ HỒ SƠ DỰ THẦU & BÁO GIÁ");

    // 5. Phòng Ban 3: Dự toán QS
    this.createWorkstation(4, 13, "Đỗ Văn Lượng", "Bóc tách CAD 8 Bill");
    this.createWorkstation(8, 13, "Vũ Đình Toàn", "Thẩm định TT 09/2024");
    this.createBookshelf(1, 13, Math.PI / 2, "KỆ BẢN VẼ HOÀN CÔNG & ĐỊNH MỨC");

    // 6. Phòng Ban 4: QA/QC
    this.createWorkstation(18, 13, "Bùi Văn Nghiệm", "17 BM QA/QC NĐ 06");
    this.createWorkstation(22, 13, "Hoàng Văn Chuẩn", "Nghiệm thu BBNTCV");
    this.createBookshelf(15.5, 13, Math.PI / 2, "KỆ PHIẾU NÉN MẪU R28 & LAS-XD");

    // 7. Phòng Ban 5: Quyết toán
    this.createWorkstation(-10, -15, "Ngô Thị Quyết", "Chiết tính Mẫu 08a");
    this.createWorkstation(-6, -15, "Đặng Đức Toán", "Kiểm toán QĐ 122/123");
    this.createBookshelf(-13.5, -15, Math.PI / 2, "KỆ HỒ SƠ THANH TOÁN 08A/08B");

    // 8. Ban Marketing & Truyền thông: Media Studio Zone
    this.createWorkstation(3, -15, "Trần Thị Lan Tỏa", "Sáng tạo PR & Social");
    this.createVideoEditingStation(7, -15, "Nguyễn Huy Dựng", "Render Video 4K & Shorts");
    this.createWorkstation(9, -12, "Lê Mai Truyền", "Thẩm định Media & Gate");
    this.createBookshelf(11.5, -15, Math.PI / 2, "KỆ THIẾT BỊ MEDIA & KỊCH BẢN");
    this.createMediaStudioProps(3, -18);

    // 9. Sảnh Lễ Tân Trung Tâm
    this.createReceptionArea(0, -2);

    // 10. Phòng Giải Trí & Wellness trong giờ giải lao
    this.createRecreationRoom(-22, -1);

    // 11. Căn Tin & Quầy Bar Doanh Nghiệp
    this.createCanteenRoom(20, -1);
  }

  // --- HÀM TẠO NỘI THẤT CHI TIẾT ---
  createWorkstation(x, z, staffName, taskNote) {
    const group = new THREE.Group();
    group.position.set(x, 0, z);

    // Mặt bàn gỗ công thái học (1.8m x 0.9m)
    const deskMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.3 });
    const deskTop = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.08, 1.0), deskMat);
    deskTop.position.set(0, 0.74, 0);
    deskTop.castShadow = true;
    group.add(deskTop);

    // Chân bàn kim loại
    const legMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.8 });
    const leg1 = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.74, 0.9), legMat);
    leg1.position.set(-0.95, 0.37, 0);
    group.add(leg1);
    const leg2 = leg1.clone();
    leg2.position.set(0.95, 0.37, 0);
    group.add(leg2);

    // Màn hình máy tính kép (Dual Monitor)
    const screenMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.2 });
    const screen1 = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.38, 0.04), screenMat);
    screen1.position.set(-0.35, 1.05, 0.25);
    screen1.rotation.y = 0.15;
    group.add(screen1);

    const screen2 = screen1.clone();
    screen2.position.set(0.35, 1.05, 0.25);
    screen2.rotation.y = -0.15;
    group.add(screen2);

    // Chân đế màn hình & Bàn phím
    const stand = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.02, 16), legMat);
    stand.position.set(0, 0.79, 0.25);
    group.add(stand);

    const kb = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.015, 0.16), new THREE.MeshStandardMaterial({ color: 0x0f172a }));
    kb.position.set(0, 0.79, -0.1);
    group.add(kb);

    // Ghế xoay văn phòng
    const chairMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.4 });
    const seat = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.08, 0.6), chairMat);
    seat.position.set(0, 0.48, -0.6);
    seat.castShadow = true;
    group.add(seat);

    const backrest = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.65, 0.08), chairMat);
    backrest.position.set(0, 0.85, -0.88);
    group.add(backrest);

    // Trụ ghế
    const cStem = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.45, 12), legMat);
    cStem.position.set(0, 0.22, -0.6);
    group.add(cStem);

    // Hồ sơ / Folder tài liệu đặt trên bàn
    const folder = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.04, 0.35), new THREE.MeshStandardMaterial({ color: 0x38bdf8 }));
    folder.position.set(0.65, 0.8, -0.1);
    group.add(folder);

    this.scene.add(group);
  }

  createVideoEditingStation(x, z, staffName, taskNote) {
    // Trạm Dựng Video & Đồ Họa Đa Phương Tiện Chuyên Nghiệp (Nguyễn Huy Dựng)
    const group = new THREE.Group();
    group.position.set(x, 0, z);

    // Bàn làm việc chữ nhật mở rộng (2.2m x 1.1m) phủ carbon đen
    const deskMat = new THREE.MeshStandardMaterial({ color: 0x1e1b4b, roughness: 0.25, metalness: 0.2 });
    const deskTop = new THREE.Mesh(new THREE.BoxGeometry(2.3, 0.08, 1.1), deskMat);
    deskTop.position.set(0, 0.74, 0);
    deskTop.castShadow = true;
    group.add(deskTop);

    // Chân bàn kim loại chữ Z thể thao
    const legMat = new THREE.MeshStandardMaterial({ color: 0xd946ef, metalness: 0.8 });
    const leg1 = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.74, 0.95), legMat);
    leg1.position.set(-1.05, 0.37, 0);
    group.add(leg1);
    const leg2 = leg1.clone();
    leg2.position.set(1.05, 0.37, 0);
    group.add(leg2);

    // Màn hình đôi cong UltraWide 4K phát sáng màu Magenta/Fuchsia rực rỡ
    const screenMat = new THREE.MeshStandardMaterial({ color: 0xd946ef, roughness: 0.1 });
    const screen1 = new THREE.Mesh(new THREE.BoxGeometry(0.85, 0.44, 0.04), screenMat);
    screen1.position.set(-0.45, 1.08, 0.28);
    screen1.rotation.y = 0.2;
    group.add(screen1);

    const screen2 = screen1.clone();
    screen2.position.set(0.45, 1.08, 0.28);
    screen2.rotation.y = -0.2;
    group.add(screen2);

    // Loa kiểm âm phòng thu âm thanh 2 bên (Studio Monitors)
    const spkMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.4 });
    const spkLeft = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.28, 0.2), spkMat);
    spkLeft.position.set(-1.0, 0.92, 0.25);
    group.add(spkLeft);
    const spkRight = spkLeft.clone();
    spkRight.position.set(1.0, 0.92, 0.25);
    group.add(spkRight);

    // Micro thu âm chuyên nghiệp (Boom Arm Mic)
    const micMat = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.9 });
    const mic = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.15, 12), micMat);
    mic.position.set(-0.6, 0.95, -0.05);
    mic.rotation.z = Math.PI / 4;
    group.add(mic);

    // Bàn phím cơ & Bàn vẽ Wacom cảm ứng
    const kb = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.015, 0.16), new THREE.MeshStandardMaterial({ color: 0x0f172a }));
    kb.position.set(-0.15, 0.79, -0.1);
    group.add(kb);

    const wacom = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.01, 0.24), new THREE.MeshStandardMaterial({ color: 0x334155 }));
    wacom.position.set(0.35, 0.79, -0.1);
    group.add(wacom);

    // Ghế gaming công thái học cao cấp
    const chairMat = new THREE.MeshStandardMaterial({ color: 0x701a75, roughness: 0.4 });
    const seat = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.08, 0.62), chairMat);
    seat.position.set(0, 0.48, -0.6);
    seat.castShadow = true;
    group.add(seat);

    const backrest = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.75, 0.08), chairMat);
    backrest.position.set(0, 0.9, -0.9);
    group.add(backrest);

    this.scene.add(group);
  }

  createMediaStudioProps(x, z) {
    // Khu vực Studio Phim Trường: Phông Xanh, Máy Quay Chân Đứng, Đèn Chiếu Softbox
    const group = new THREE.Group();
    group.position.set(x, 0, z);

    // 1. Phông Xanh Quay Phim Chuẩn Chroma Key (Green Screen Backdrop)
    const greenMat = new THREE.MeshStandardMaterial({ color: 0x22c55e, roughness: 0.6 });
    const backdrop = new THREE.Mesh(new THREE.BoxGeometry(3.6, 2.6, 0.06), greenMat);
    backdrop.position.set(0, 1.35, -1.8);
    backdrop.castShadow = true;
    group.add(backdrop);

    // Khung kim loại đỡ phông xanh
    const frameMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.9 });
    const fTop = new THREE.Mesh(new THREE.BoxGeometry(3.8, 0.06, 0.06), frameMat);
    fTop.position.set(0, 2.68, -1.8);
    group.add(fTop);

    const fLeg1 = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 2.7, 12), frameMat);
    fLeg1.position.set(-1.85, 1.35, -1.8);
    group.add(fLeg1);
    const fLeg2 = fLeg1.clone();
    fLeg2.position.set(1.85, 1.35, -1.8);
    group.add(fLeg2);

    // 2. Chân Máy Quay Phim Chuyên Dụng 4K (Tripod Cinema Camera)
    const camGroup = new THREE.Group();
    camGroup.position.set(0, 0, 0.2);

    // Chân tripod 3 càng
    for (let i = 0; i < 3; i++) {
      const angle = (i * Math.PI * 2) / 3;
      const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 1.3, 8), frameMat);
      leg.position.set(Math.cos(angle) * 0.35, 0.65, Math.sin(angle) * 0.35);
      leg.rotation.z = Math.cos(angle) * -0.22;
      leg.rotation.x = Math.sin(angle) * 0.22;
      camGroup.add(leg);
    }

    // Thân máy quay Cinema
    const camBodyMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.7 });
    const camBody = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.22, 0.38), camBodyMat);
    camBody.position.set(0, 1.38, 0);
    camGroup.add(camBody);

    // Ống kính máy quay (Lens) hướng vào phông xanh
    const lensMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, metalness: 0.9, roughness: 0.1 });
    const lens = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.08, 0.22, 16), lensMat);
    lens.position.set(0, 1.38, -0.26);
    lens.rotation.x = Math.PI / 2;
    camGroup.add(lens);

    group.add(camGroup);

    // 3. Đèn Studio Softbox Chiếu Sáng Chuyên Dụng
    const lightGroup = new THREE.Group();
    lightGroup.position.set(-1.5, 0, -0.6);

    const lPole = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 2.1, 12), frameMat);
    lPole.position.set(0, 1.05, 0);
    lightGroup.add(lPole);

    // Chóa đèn bát giác (Softbox Hood)
    const softboxMat = new THREE.MeshStandardMaterial({ color: 0xfef08a, emissive: 0xfef08a, emissiveIntensity: 0.6 });
    const softbox = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.65, 0.25), softboxMat);
    softbox.position.set(0, 2.05, 0);
    softbox.rotation.y = Math.PI / 4;
    softbox.rotation.x = 0.2;
    lightGroup.add(softbox);

    const studioPoint = new THREE.PointLight(0xfef08a, 0.9, 15);
    studioPoint.position.set(0, 2.1, 0.2);
    lightGroup.add(studioPoint);

    group.add(lightGroup);

    this.scene.add(group);
  }

  createExecutiveDesk(x, z) {
    // Bàn Tổng Giám Đốc gỗ óc chó chữ L
    const group = new THREE.Group();
    group.position.set(x, 0, z);

    const walnutMat = new THREE.MeshStandardMaterial({ color: 0x3f1d11, roughness: 0.3, metalness: 0.1 });
    const deskMain = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.12, 1.4), walnutMat);
    deskMain.position.set(0, 0.78, 0);
    deskMain.castShadow = true;
    group.add(deskMain);

    const deskSide = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.1, 2.0), walnutMat);
    deskSide.position.set(-1.0, 0.73, 1.2);
    group.add(deskSide);

    // Chân bàn nguyên khối sang trọng
    const leg1 = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.78, 1.3), walnutMat);
    leg1.position.set(1.5, 0.39, 0);
    group.add(leg1);
    const leg2 = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.78, 1.3), walnutMat);
    leg2.position.set(-1.5, 0.39, 0);
    group.add(leg2);

    // Màn hình iMac lớn màu bạc
    const imacMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.9, roughness: 0.1 });
    const imac = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.65, 0.04), imacMat);
    imac.position.set(0, 1.25, 0.3);
    group.add(imac);

    // Ghế Chủ Tịch bọc da VIP
    const leatherMat = new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.2 });
    const vipSeat = new THREE.Mesh(new THREE.BoxGeometry(0.75, 0.12, 0.75), leatherMat);
    vipSeat.position.set(0, 0.5, -0.85);
    group.add(vipSeat);
    const vipBack = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.95, 0.12), leatherMat);
    vipBack.position.set(0, 1.05, -1.2);
    group.add(vipBack);

    // Cờ để bàn & tượng phong thủy
    const flagPole = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.45), imacMat);
    flagPole.position.set(1.2, 1.02, 0.2);
    group.add(flagPole);

    this.scene.add(group);
  }

  createMeetingRoom(cx, cz) {
    const group = new THREE.Group();
    group.position.set(cx, 0, cz);

    // Bàn họp lớn Oval (Dài 8m x Rộng 2.6m)
    const meetMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.25, metalness: 0.2 });
    const tableTop = new THREE.Mesh(new THREE.CylinderGeometry(1.3, 1.3, 0.1, 32), meetMat);
    tableTop.scale.set(3.2, 1, 1); // Kéo dài thành hình oval
    tableTop.position.set(0, 0.75, 0);
    tableTop.castShadow = true;
    group.add(tableTop);

    // Chân bàn tròn kim loại
    const legMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, metalness: 0.8 });
    const leg1 = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.35, 0.75, 24), legMat);
    leg1.position.set(-2.2, 0.375, 0);
    group.add(leg1);
    const leg2 = leg1.clone();
    leg2.position.set(2.2, 0.375, 0);
    group.add(leg2);

    // 12 Ghế họp xung quanh bàn
    const chairMat = new THREE.MeshStandardMaterial({ color: 0x334155 });
    for (let i = 0; i < 5; i++) {
      // Dãy ghế bên trên
      const c1 = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.08, 0.5), chairMat);
      c1.position.set(-2.8 + i * 1.4, 0.48, 1.6);
      group.add(c1);
      // Dãy ghế bên dưới
      const c2 = c1.clone();
      c2.position.set(-2.8 + i * 1.4, 0.48, -1.6);
      group.add(c2);
    }
    // 2 ghế đầu bàn
    const cHead1 = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.08, 0.5), chairMat);
    cHead1.position.set(-4.0, 0.48, 0);
    group.add(cHead1);
    const cHead2 = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.08, 0.5), chairMat);
    cHead2.position.set(4.0, 0.48, 0);
    group.add(cHead2);

    // Màn hình trình chiếu TV lớn 85 inch treo tường
    const tvMat = new THREE.MeshStandardMaterial({ color: 0x0f172a });
    const tv = new THREE.Mesh(new THREE.BoxGeometry(3.6, 2.0, 0.08), tvMat);
    tv.position.set(0, 2.6, -5.8);
    group.add(tv);

    // Màn hình hiển thị bản vẽ CAD / tiến độ dự án
    const tvScreenMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
    const tvScreen = new THREE.Mesh(new THREE.PlaneGeometry(3.4, 1.8), tvScreenMat);
    tvScreen.position.set(0, 2.6, -5.73);
    group.add(tvScreen);

    this.scene.add(group);
  }

  createBookshelf(x, z, rotY = 0, title = "") {
    const group = new THREE.Group();
    group.position.set(x, 0, z);
    group.rotation.y = rotY;

    // Kệ sách 4 tầng (Rộng 2.4m x Cao 3.2m x Sâu 0.5m)
    const woodMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.4 });
    const frame = new THREE.Mesh(new THREE.BoxGeometry(2.4, 3.2, 0.5), woodMat);
    frame.position.set(0, 1.6, 0);
    frame.castShadow = true;
    group.add(frame);

    // Từng tập tài liệu màu sắc xếp trên kệ (Hồ sơ pháp lý, HSMT, BOQ, Mẫu 08a)
    const bookColors = [0x3b82f6, 0xef4444, 0x10b981, 0xf59e0b, 0x8b5cf6, 0x06b6d4];
    for (let shelf = 0; shelf < 4; shelf++) {
      for (let b = 0; b < 7; b++) {
        const bCol = bookColors[(shelf + b) % bookColors.length];
        const binder = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.38, 0.32), new THREE.MeshStandardMaterial({ color: bCol }));
        binder.position.set(-0.8 + b * 0.24, 0.6 + shelf * 0.75, 0.05);
        group.add(binder);
      }
    }

    this.scene.add(group);
  }

  createPlant(x, z) {
    const group = new THREE.Group();
    group.position.set(x, 0, z);

    // Chậu sứ trắng
    const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.25, 0.7, 16), new THREE.MeshStandardMaterial({ color: 0xf8fafc }));
    pot.position.set(0, 0.35, 0);
    group.add(pot);

    // Lá cây xanh tươi
    const leafMat = new THREE.MeshStandardMaterial({ color: 0x15803d, roughness: 0.3 });
    for (let i = 0; i < 5; i++) {
      const leaf = new THREE.Mesh(new THREE.SphereGeometry(0.35, 8, 8), leafMat);
      leaf.scale.set(0.6, 1.4, 0.4);
      leaf.position.set((Math.random() - 0.5) * 0.3, 0.85 + i * 0.25, (Math.random() - 0.5) * 0.3);
      group.add(leaf);
    }
    this.scene.add(group);
  }

  createExecutiveSofa(x, z) {
    const group = new THREE.Group();
    group.position.set(x, 0, z);

    const sofaMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.5 });
    const seat = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.4, 0.8), sofaMat);
    seat.position.set(0, 0.2, 0);
    group.add(seat);

    const back = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.5, 0.25), sofaMat);
    back.position.set(0, 0.55, -0.3);
    group.add(back);

    // Bàn trà kính nhỏ
    const teaTable = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 0.35, 24), new THREE.MeshStandardMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.6 }));
    teaTable.position.set(0, 0.18, 0.9);
    group.add(teaTable);

    this.scene.add(group);
  }

  createReceptionArea(x, z) {
    const group = new THREE.Group();
    group.position.set(x, 0, z);

    // Quầy lễ tân cong chữ U (Reception Counter)
    const counterMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.2, metalness: 0.3 });
    const counter = new THREE.Mesh(new THREE.CylinderGeometry(3.5, 3.5, 1.15, 32, 1, false, 0, Math.PI), counterMat);
    counter.position.set(0, 0.58, 0);
    counter.rotation.y = Math.PI;
    group.add(counter);

    // Logo T&T nổi phát sáng
    this.createGlowSignboard("🏢 T&T ONE-PERSON AI FIRM", x, 2.4, z - 2.5, 0x10b981);
    this.scene.add(group);
  }

  createRecreationRoom(cx, cz) {
    // PHÒNG GIẢI TRÍ & CHĂM SÓC SỨC KHỎE NHÂN VIÊN (Recreation & Wellness Lounge)
    const group = new THREE.Group();
    group.position.set(cx, 0, cz);

    // 1. Tivi Giải Trí Lớn 85 inch & Kệ TV / Console Gaming
    const tvMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.8 });
    const tvFrame = new THREE.Mesh(new THREE.BoxGeometry(3.6, 2.0, 0.08), tvMat);
    tvFrame.position.set(0, 2.5, -4.2);
    group.add(tvFrame);

    const tvScreenMat = new THREE.MeshStandardMaterial({
      color: 0x6366f1,
      emissive: 0x6366f1,
      emissiveIntensity: 0.6,
      roughness: 0.2
    });
    const tvScreen = new THREE.Mesh(new THREE.PlaneGeometry(3.4, 1.8), tvScreenMat);
    tvScreen.position.set(0, 2.5, -4.13);
    group.add(tvScreen);

    // Kệ tủ TV gỗ sang trọng
    const cabinetMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.4 });
    const cabinet = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.45, 0.7), cabinetMat);
    cabinet.position.set(0, 0.225, -3.9);
    group.add(cabinet);

    // Máy chơi game console (PlayStation) & tay cầm
    const consoleMesh = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.08, 0.25), new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.2 }));
    consoleMesh.position.set(0, 0.49, -3.9);
    group.add(consoleMesh);

    // 2. 02 Ghế Massage Toàn Thân Thông Minh (Zero-Gravity Massage Chairs)
    const createMassageChair = (x, z, rotY) => {
      const chairGroup = new THREE.Group();
      chairGroup.position.set(x, 0, z);
      chairGroup.rotation.y = rotY;

      const leatherMat = new THREE.MeshStandardMaterial({ color: 0x3e2723, roughness: 0.35 });

      // Đế ghế nâng hạ
      const base = new THREE.Mesh(new THREE.BoxGeometry(0.85, 0.22, 1.4), new THREE.MeshStandardMaterial({ color: 0x18181b, metalness: 0.6 }));
      base.position.set(0, 0.11, 0);
      chairGroup.add(base);

      // Thân đệm ghế nghiêng góc thư giãn
      const seat = new THREE.Mesh(new THREE.BoxGeometry(0.75, 0.3, 0.8), leatherMat);
      seat.position.set(0, 0.35, 0.1);
      chairGroup.add(seat);

      // Tựa lưng uốn lượn công thái học
      const back = new THREE.Mesh(new THREE.BoxGeometry(0.75, 0.9, 0.22), leatherMat);
      back.position.set(0, 0.8, -0.35);
      back.rotation.x = -0.3;
      chairGroup.add(back);

      // Đệm đầu massage cổ
      const pillow = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.2, 0.12), new THREE.MeshStandardMaterial({ color: 0xd97706, roughness: 0.5 }));
      pillow.position.set(0, 1.25, -0.48);
      chairGroup.add(pillow);

      // 2 Tay vịn massage cánh tay
      const armL = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.45, 0.9), leatherMat);
      armL.position.set(-0.45, 0.5, 0.05);
      chairGroup.add(armL);
      const armR = armL.clone();
      armR.position.set(0.45, 0.5, 0.05);
      chairGroup.add(armR);

      // Bảng điều khiển cảm ứng LED phát sáng xanh lam
      const tablet = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.02, 0.18), new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x38bdf8, emissiveIntensity: 0.8 }));
      tablet.position.set(0.48, 0.74, 0.15);
      chairGroup.add(tablet);

      // Phần massage bắp chân & bàn chân (Footrest)
      const footrest = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.4, 0.45), leatherMat);
      footrest.position.set(0, 0.3, 0.65);
      chairGroup.add(footrest);

      return chairGroup;
    };

    group.add(createMassageChair(-3.8, -1.2, Math.PI / 4));
    group.add(createMassageChair(-3.8, 1.8, -Math.PI / 6));

    // 3. Thiết Bị Thể Dục: 02 Máy Chạy Bộ Điện Tử Hiện Đại (Treadmills)
    const createTreadmill = (x, z) => {
      const tmGroup = new THREE.Group();
      tmGroup.position.set(x, 0, z);

      const metalMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.8 });
      const beltMat = new THREE.MeshStandardMaterial({ color: 0x09090b, roughness: 0.8 });

      // Băng chuyền chạy bộ
      const base = new THREE.Mesh(new THREE.BoxGeometry(0.85, 0.14, 1.9), metalMat);
      base.position.set(0, 0.07, 0);
      tmGroup.add(base);

      const belt = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.02, 1.7), beltMat);
      belt.position.set(0, 0.15, 0);
      tmGroup.add(belt);

      // 2 Trụ đỡ đứng
      const pole1 = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.2), metalMat);
      pole1.position.set(-0.38, 0.65, -0.75);
      pole1.rotation.x = 0.2;
      tmGroup.add(pole1);
      const pole2 = pole1.clone();
      pole2.position.set(0.38, 0.65, -0.75);
      tmGroup.add(pole2);

      // Bảng điều khiển điện tử LED + Tay vịn
      const display = new THREE.Mesh(new THREE.BoxGeometry(0.78, 0.22, 0.16), new THREE.MeshStandardMaterial({ color: 0x10b981, emissive: 0x10b981, emissiveIntensity: 0.5 }));
      display.position.set(0, 1.2, -0.65);
      tmGroup.add(display);

      return tmGroup;
    };

    group.add(createTreadmill(4.2, -1.5));
    group.add(createTreadmill(4.2, 1.5));

    // 4. Khu Vực Thảm Tập Yoga & Tạ Tay Thể Lực
    const matMesh = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.02, 2.0), new THREE.MeshStandardMaterial({ color: 0xa855f7, roughness: 0.6 }));
    matMesh.position.set(1.5, 0.01, -1.5);
    group.add(matMesh);

    // Bóng tập Gym Swiss Ball tròn
    const ballMesh = new THREE.Mesh(new THREE.SphereGeometry(0.38, 16, 16), new THREE.MeshStandardMaterial({ color: 0x06b6d4, roughness: 0.3 }));
    ballMesh.position.set(1.5, 0.38, -0.2);
    group.add(ballMesh);

    // Giá để tạ tay mini
    const rackMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.9 });
    const rack = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.4, 0.3), rackMat);
    rack.position.set(1.5, 0.2, 1.5);
    group.add(rack);

    // 5. Bộ Ghế Sofa Thư Giãn Lười & Bàn Trà Kính
    const sofaMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.5 });
    const sofaSeat = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.35, 0.9), sofaMat);
    sofaSeat.position.set(-0.2, 0.18, 2.2);
    group.add(sofaSeat);

    const sofaBack = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.5, 0.25), sofaMat);
    sofaBack.position.set(-0.2, 0.55, 2.65);
    group.add(sofaBack);

    const teaTable = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.45, 0.32, 24), new THREE.MeshStandardMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.6 }));
    teaTable.position.set(-0.2, 0.16, 1.2);
    group.add(teaTable);

    this.scene.add(group);
  }

  createCanteenRoom(cx, cz) {
    // PHÒNG CĂN TIN & QUẦY BAR DOANH NGHIỆP (Canteen & Cafeteria Bar Lounge)
    const group = new THREE.Group();
    group.position.set(cx, 0, cz);

    // 1. Quầy Bar Phục Vụ Ẩm Thực & Cà Phê (Bar Counter - Dài 4.8m)
    const marbleMat = new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.15, metalness: 0.2 });
    const woodMat = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.4 });
    const chromeMat = new THREE.MeshStandardMaterial({ color: 0xcbd5e1, metalness: 0.9, roughness: 0.1 });

    // Mặt quầy bar đá marble đen ánh kim
    const barTop = new THREE.Mesh(new THREE.BoxGeometry(4.8, 0.08, 0.85), marbleMat);
    barTop.position.set(0, 1.15, -1.8);
    barTop.castShadow = true;
    group.add(barTop);

    // Thân quầy bar ốp gỗ cao cấp
    const barBody = new THREE.Mesh(new THREE.BoxGeometry(4.7, 1.1, 0.75), woodMat);
    barBody.position.set(0, 0.55, -1.8);
    barBody.castShadow = true;
    group.add(barBody);

    // Kệ tủ rượu / đồ uống phía sau quầy bar (Back Bar Shelf)
    const backShelf = new THREE.Mesh(new THREE.BoxGeometry(4.8, 2.2, 0.4), new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.6 }));
    backShelf.position.set(0, 1.5, -4.1);
    group.add(backShelf);

    // Các tầng kệ trưng bày ly tách và chai đồ uống
    for (let i = 0; i < 3; i++) {
      const shelfTier = new THREE.Mesh(new THREE.BoxGeometry(4.6, 0.04, 0.35), new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.8 }));
      shelfTier.position.set(0, 0.8 + i * 0.6, -4.0);
      group.add(shelfTier);
    }

    // Máy pha cà phê Espresso chuyên nghiệp inox
    const coffeeMachineMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.95, roughness: 0.1 });
    const coffeeMachine = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.48, 0.45), coffeeMachineMat);
    coffeeMachine.position.set(-1.2, 1.42, -1.8);
    group.add(coffeeMachine);

    // Tủ mát kính mini trưng bày nước ngọt & bánh ngọt
    const glassCoolerMat = new THREE.MeshPhysicalMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.45, roughness: 0.1 });
    const cooler = new THREE.Mesh(new THREE.BoxGeometry(0.85, 0.55, 0.48), glassCoolerMat);
    cooler.position.set(1.2, 1.45, -1.8);
    group.add(cooler);

    // 2. 04 Ghế Quầy Bar Chân Cao (Bar Stools)
    const stoolMat = new THREE.MeshStandardMaterial({ color: 0xea580c, roughness: 0.4 });
    const stoolPositions = [-1.8, -0.6, 0.6, 1.8];

    stoolPositions.forEach((sx) => {
      const sGroup = new THREE.Group();
      sGroup.position.set(sx, 0, -0.9);

      // Đệm ngồi bọc da tròn
      const seat = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.08, 16), stoolMat);
      seat.position.set(0, 0.82, 0);
      sGroup.add(seat);

      // Trụ kim loại mạ chrome
      const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.8, 12), chromeMat);
      stem.position.set(0, 0.4, 0);
      sGroup.add(stem);

      // Chân đế tròn
      const base = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.03, 16), chromeMat);
      base.position.set(0, 0.015, 0);
      sGroup.add(base);

      group.add(sGroup);
    });

    // 3. 02 Cụm Bàn Ăn Căn Tin Tròn Cho Nhân Viên
    const createDiningTable = (x, z) => {
      const tGroup = new THREE.Group();
      tGroup.position.set(x, 0, z);

      // Mặt bàn gỗ tròn đường kính 1.4m
      const tableTop = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.7, 0.06, 24), new THREE.MeshStandardMaterial({ color: 0x92400e, roughness: 0.3 }));
      tableTop.position.set(0, 0.74, 0);
      tableTop.castShadow = true;
      tGroup.add(tableTop);

      // Trụ bàn
      const tStem = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.74, 16), chromeMat);
      tStem.position.set(0, 0.37, 0);
      tGroup.add(tStem);

      // 4 Ghế ăn xung quanh
      const chairMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.5 });
      for (let i = 0; i < 4; i++) {
        const angle = (i * Math.PI) / 2;
        const cMesh = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.06, 0.42), chairMat);
        cMesh.position.set(Math.cos(angle) * 0.95, 0.46, Math.sin(angle) * 0.95);
        tGroup.add(cMesh);

        const cBack = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.45, 0.05), chairMat);
        cBack.position.set(Math.cos(angle) * 1.15, 0.7, Math.sin(angle) * 1.15);
        cBack.rotation.y = -angle + Math.PI / 2;
        tGroup.add(cBack);
      }

      return tGroup;
    };

    group.add(createDiningTable(-4.0, 1.8));
    group.add(createDiningTable(3.8, 1.8));

    // 4. Cây Nước Uống Tự Động Nóng Lạnh
    const dispenserMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.2 });
    const dispenser = new THREE.Mesh(new THREE.BoxGeometry(0.42, 1.2, 0.42), dispenserMat);
    dispenser.position.set(-6.5, 0.6, -1.8);
    group.add(dispenser);

    // Bình nước xanh úp trên cây nước
    const bottle = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.45, 16), new THREE.MeshPhysicalMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.7 }));
    bottle.position.set(-6.5, 1.42, -1.8);
    group.add(bottle);

    this.scene.add(group);
  }

  // --- TẠO 11 NHÂN SỰ AI 3D (HUMANOID AVATARS) ---
  spawnStaffAvatars() {
    this.STAFF_DATA.forEach((s) => {
      const avatar = this.createHumanoidMesh(s);
      avatar.userData = {
        staffId: s.id,
        name: s.name,
        role: s.role,
        level: s.level,
        dept: s.dept,
        deskPos: s.deskPos,
        meetPos: s.meetPos,
        isMoving: false,
        targetPos: null,
        walkSpeed: 4.5,
        idleTimer: Math.random() * 5
      };

      // Đặt nhân sự tại vị trí bàn làm việc ban đầu
      avatar.position.set(s.deskPos.x, 0, s.deskPos.z);
      avatar.rotation.y = s.deskPos.rot;

      this.scene.add(avatar);
      this.staffMembers.push(avatar);
      this.selectableObjects.push(avatar);
    });
  }

  createHumanoidMesh(staffInfo) {
    const group = new THREE.Group();

    // 1. Đầu (Head)
    const skinMat = new THREE.MeshStandardMaterial({ color: 0xfbbf24, roughness: 0.5 });
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.22, 16, 16), skinMat);
    head.position.y = 1.55;
    head.castShadow = true;
    group.add(head);

    // Tóc / Nón kỹ sư (nếu là QA/QC hoặc QS)
    if (staffInfo.dept === "QAQC" || staffInfo.dept === "QS") {
      const helmetMat = new THREE.MeshStandardMaterial({ color: staffInfo.dept === "QAQC" ? 0xffffff : 0xfbbf24, roughness: 0.2 });
      const helmet = new THREE.Mesh(new THREE.SphereGeometry(0.24, 16, 16, 0, Math.PI * 2, 0, Math.PI / 2), helmetMat);
      helmet.position.y = 1.62;
      group.add(helmet);
    } else {
      const hairMat = new THREE.MeshStandardMaterial({ color: 0x18181b });
      const hair = new THREE.Mesh(new THREE.SphereGeometry(0.23, 16, 16, 0, Math.PI * 2, 0, Math.PI / 2), hairMat);
      hair.position.y = 1.62;
      group.add(hair);
    }

    // 2. Thân (Torso: Áo vest hoặc sơ mi)
    const suitMat = new THREE.MeshStandardMaterial({ color: staffInfo.color, roughness: 0.4 });
    const torso = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.2, 0.65, 12), suitMat);
    torso.position.y = 1.05;
    torso.castShadow = true;
    group.add(torso);

    // Cà vạt (Tie)
    const tie = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.35, 0.04), new THREE.MeshStandardMaterial({ color: 0xef4444 }));
    tie.position.set(0, 1.1, 0.21);
    group.add(tie);

    // 3. Tay (Arms)
    const armGeo = new THREE.CylinderGeometry(0.07, 0.07, 0.55, 8);
    const leftArm = new THREE.Mesh(armGeo, suitMat);
    leftArm.position.set(-0.32, 1.05, 0);
    leftArm.rotation.z = 0.15;
    group.add(leftArm);

    const rightArm = new THREE.Mesh(armGeo, suitMat);
    rightArm.position.set(0.32, 1.05, 0);
    rightArm.rotation.z = -0.15;
    group.add(rightArm);

    // 4. Chân (Legs)
    const pantsMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.6 });
    const legGeo = new THREE.CylinderGeometry(0.09, 0.08, 0.72, 8);
    const leftLeg = new THREE.Mesh(legGeo, pantsMat);
    leftLeg.position.set(-0.13, 0.36, 0);
    leftLeg.castShadow = true;
    group.add(leftLeg);

    const rightLeg = new THREE.Mesh(legGeo, pantsMat);
    rightLeg.position.set(0.13, 0.36, 0);
    rightLeg.castShadow = true;
    group.add(rightLeg);

    // 5. Nameplate Hologram lơ lửng trên đầu
    this.attachNameplate(group, staffInfo.name, staffInfo.level, staffInfo.color);

    return group;
  }

  attachNameplate(avatarGroup, name, level, colorHex) {
    const canvas = document.createElement("canvas");
    canvas.width = 256;
    canvas.height = 64;
    const ctx = canvas.getContext("2d");

    ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
    ctx.roundRect(2, 2, 252, 60, 12);
    ctx.fill();

    ctx.strokeStyle = `#${colorHex.toString(16).padStart(6, "0")}`;
    ctx.lineWidth = 4;
    ctx.roundRect(2, 2, 252, 60, 12);
    ctx.stroke();

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 20px Arial";
    ctx.textAlign = "center";
    ctx.fillText(name, 128, 28);

    ctx.fillStyle = "#38bdf8";
    ctx.font = "14px Arial";
    ctx.fillText(`[${level}]`, 128, 50);

    const texture = new THREE.CanvasTexture(canvas);
    const mat = new THREE.SpriteMaterial({ map: texture, transparent: true });
    const sprite = new THREE.Sprite(mat);
    sprite.scale.set(1.8, 0.45, 1);
    sprite.position.y = 2.15;
    avatarGroup.add(sprite);
  }

  // --- HÀM TƯƠNG TÁC ĐIỀU KHIỂN & DI CHUYỂN NHÂN SỰ ---
  onPointerClick(event) {
    const rect = this.renderer.domElement.getBoundingClientRect();
    this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    this.raycaster.setFromCamera(this.mouse, this.camera);
    const intersects = this.raycaster.intersectObjects(this.selectableObjects, true);

    if (intersects.length > 0) {
      // Tìm avatar cha của đối tượng được click
      let obj = intersects[0].object;
      while (obj.parent && !obj.userData.staffId) {
        obj = obj.parent;
      }
      if (obj.userData.staffId) {
        this.selectStaff(obj);
        return;
      }
    }

    // Nếu click vào mặt sàn khi đã chọn nhân sự -> Di chuyển nhân sự đến điểm click (Click-to-Move)
    if (this.selectedStaff) {
      const planeIntersects = this.raycaster.intersectObject(this.scene.children.find((c) => c.isMesh && c.geometry.type === "PlaneGeometry"));
      if (planeIntersects.length > 0) {
        const pt = planeIntersects[0].point;
        this.moveStaffToPoint(this.selectedStaff, { x: pt.x, z: pt.z });
      }
    }
  }

  selectStaff(staffAvatar) {
    this.selectedStaff = staffAvatar;
    const data = staffAvatar.userData;

    // Hiển thị Card Hologram trên UI HTML
    if (typeof window.showStaffModal3D === "function") {
      window.showStaffModal3D(data);
    }
  }

  moveStaffToPoint(avatar, target) {
    avatar.userData.isMoving = true;
    avatar.userData.targetPos = target;
  }

  // Lệnh tập hợp toàn bộ nhân sự vào phòng họp lớn
  gatherAllToMeeting() {
    this.isMeetingMode = true;
    this.staffMembers.forEach((avatar) => {
      this.moveStaffToPoint(avatar, avatar.userData.meetPos);
    });
  }

  // Lệnh toàn bộ nhân sự quay về bàn làm việc của mình
  sendAllBackToDesks() {
    this.isMeetingMode = false;
    this.staffMembers.forEach((avatar) => {
      this.moveStaffToPoint(avatar, avatar.userData.deskPos);
    });
  }

  // Lệnh toàn bộ nhân sự nghỉ ngơi giải lao (Căn tin, Massage, Gym Wellness)
  gatherAllToBreak() {
    this.isMeetingMode = false;
    const breakSpots = [
      // Phân bổ vào Phòng Giải Trí & Wellness
      { x: -18, z: -2.5, rot: 0 },
      { x: -16, z: -2.5, rot: 0 },
      { x: -25.5, z: 2.0, rot: Math.PI },
      { x: -23.5, z: 2.0, rot: Math.PI },
      { x: -23, z: 0.5, rot: -Math.PI / 2 },
      { x: -21, z: 0.5, rot: Math.PI / 2 },
      { x: -25.5, z: -2.2, rot: 0 },
      // Phân bổ vào Căn Tin & Quầy Bar
      { x: 17.6, z: -1.0, rot: -Math.PI / 2 },
      { x: 19.2, z: -1.0, rot: -Math.PI / 2 },
      { x: 20.8, z: -1.0, rot: -Math.PI / 2 },
      { x: 22.4, z: -1.0, rot: -Math.PI / 2 },
      { x: 16.5, z: 0.8, rot: 0 },
      { x: 16.5, z: 2.8, rot: Math.PI },
      { x: 23.5, z: 0.8, rot: 0 },
      { x: 23.5, z: 2.8, rot: Math.PI }
    ];

    let spotIdx = 0;
    this.staffMembers.forEach((avatar) => {
      // 2 nhân viên quầy bar và bếp trưởng ở lại vị trí phục vụ
      if (avatar.userData.staffId === 'canteen_barista' || avatar.userData.staffId === 'canteen_chef') {
        this.moveStaffToPoint(avatar, avatar.userData.deskPos);
        return;
      }
      const spot = breakSpots[spotIdx % breakSpots.length];
      spotIdx++;
      this.moveStaffToPoint(avatar, spot);
    });
  }

  // Di chuyển Camera đến khu vực chỉ định
  focusZone(zoneKey) {
    const zone = this.ZONES[zoneKey];
    if (!zone || !this.controls) return;

    const tx = zone.center.x;
    const tz = zone.center.z;

    this.controls.target.set(tx, 1, tz);
    this.camera.position.set(tx, 16, tz + 22);
    this.controls.update();
  }

  toggleDayNight() {
    this.isNightMode = !this.isNightMode;
    if (this.isNightMode) {
      this.scene.background = new THREE.Color(0x030712);
      this.sunLight.intensity = 0.2;
      this.ambientLight.intensity = 0.35;
    } else {
      this.scene.background = new THREE.Color(0x0a0f1d);
      this.sunLight.intensity = 1.1;
      this.ambientLight.intensity = 0.7;
    }
  }

  // --- ANIMATION UPDATE LOOP ---
  animate() {
    requestAnimationFrame(() => this.animate());

    const delta = this.clock.getDelta();

    // Cập nhật di chuyển cho nhân sự (Interpolation walk)
    this.staffMembers.forEach((avatar) => {
      const u = avatar.userData;
      if (u.isMoving && u.targetPos) {
        const dx = u.targetPos.x - avatar.position.x;
        const dz = u.targetPos.z - avatar.position.z;
        const dist = Math.sqrt(dx * dx + dz * dz);

        if (dist > 0.2) {
          const moveDist = Math.min(u.walkSpeed * delta, dist);
          avatar.position.x += (dx / dist) * moveDist;
          avatar.position.z += (dz / dist) * moveDist;

          // Xoay mặt theo hướng đi
          avatar.rotation.y = Math.atan2(dx, dz);

          // Nhấp nhô bước chân nhẹ (Walking bobbing)
          avatar.position.y = Math.abs(Math.sin(this.clock.getElapsedTime() * 10)) * 0.08;
        } else {
          avatar.position.x = u.targetPos.x;
          avatar.position.z = u.targetPos.z;
          avatar.position.y = 0;
          u.isMoving = false;
          u.targetPos = null;
        }
      } else if (!this.isMeetingMode) {
        // Tuần tra tự do nhẹ khi rảnh rỗi (Idle wandering near desk)
        u.idleTimer -= delta;
        if (u.idleTimer <= 0) {
          u.idleTimer = 10 + Math.random() * 15;
          // Đi lại quanh bàn làm việc bán kính 1.5m
          const ox = u.deskPos.x + (Math.random() - 0.5) * 2.0;
          const oz = u.deskPos.z + (Math.random() - 0.5) * 2.0;
          this.moveStaffToPoint(avatar, { x: ox, z: oz });
        }
      }
    });

    if (this.controls) {
      this.controls.update();
    }

    this.renderer.render(this.scene, this.camera);
  }

  onWindowResize() {
    if (!this.container || !this.renderer || !this.camera) return;
    const w = this.container.clientWidth;
    const h = this.container.clientHeight;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }
}

// Global instance launcher
window.Office3DFloorEngine = Office3DFloorEngine;
window.office3DInstance = null;
