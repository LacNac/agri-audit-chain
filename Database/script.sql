-- =====================================================================
-- SCRIPT TẠO DATABASE HỆ THỐNG QUẢN LÝ KIỂM ĐỊNH LÔ HÀNG
-- Dựa theo sơ đồ ERD: User, Roles, Batches, Audit_request,
--                      Audit_reports, Qr_codes
-- (Đã sửa quan hệ Batches-Audit_request thành 1-N cho đúng logic khóa ngoại,
--  và bổ sung FK id_auditor -> User, cột created_at để truy vết)
-- Dialect: MySQL 8.0+
-- =====================================================================

DROP DATABASE IF EXISTS quality_audit_system;
CREATE DATABASE quality_audit_system
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE quality_audit_system;

-- ---------------------------------------------------------------------
-- 1. Bảng Roles (vai trò người dùng: admin, staff, auditor, ...)
-- ---------------------------------------------------------------------
CREATE TABLE Roles (
    id_role     INT AUTO_INCREMENT PRIMARY KEY,
    role_name   VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 2. Bảng User
-- Quan hệ: Roles (1) - (N) User
-- ---------------------------------------------------------------------
CREATE TABLE User (
    id_user     INT AUTO_INCREMENT PRIMARY KEY,
    Name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    id_role     INT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_role
        FOREIGN KEY (id_role) REFERENCES Roles(id_role)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 3. Bảng Batches (lô sản phẩm)
-- ---------------------------------------------------------------------
CREATE TABLE Batches (
    id_batch      INT AUTO_INCREMENT PRIMARY KEY,
    product_name  VARCHAR(150) NOT NULL,
    audit_status  VARCHAR(50) NOT NULL DEFAULT 'pending'
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 4. Bảng Audit_request (yêu cầu kiểm định)
-- Quan hệ: Batches (1) - (N) Audit_request   [đã sửa lại chiều cho đúng FK]
--          User    (1) - (N) Audit_request   (id_user = người gửi kiểm định)
-- ---------------------------------------------------------------------
CREATE TABLE Audit_request (
    id_audit    INT AUTO_INCREMENT PRIMARY KEY,
    id_batch    INT NOT NULL,
    id_user     INT NOT NULL,           -- người gửi yêu cầu kiểm định
    status      VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_request_batch
        FOREIGN KEY (id_batch) REFERENCES Batches(id_batch)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_audit_request_user
        FOREIGN KEY (id_user) REFERENCES User(id_user)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 5. Bảng Audit_reports (báo cáo kết quả kiểm định)
-- Quan hệ: Audit_request (1) - (1) Audit_reports
--          User (auditor) (1) - (N) Audit_reports  [FK ngầm, bổ sung thêm]
-- ---------------------------------------------------------------------
CREATE TABLE Audit_reports (
    id_report   INT AUTO_INCREMENT PRIMARY KEY,   -- sửa lỗi chính tả id_repost -> id_report
    id_request  INT NOT NULL UNIQUE,              -- UNIQUE để đảm bảo quan hệ 1-1
    file        VARCHAR(255),
    result      VARCHAR(255),
    id_auditor  INT NOT NULL,                     -- người thực hiện kiểm định
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_report_request
        FOREIGN KEY (id_request) REFERENCES Audit_request(id_audit)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_report_auditor
        FOREIGN KEY (id_auditor) REFERENCES User(id_user)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 6. Bảng Qr_codes (mã QR gắn với lô hàng)
-- Quan hệ: Batches (1) - (1) Qr_codes
-- ---------------------------------------------------------------------
CREATE TABLE Qr_codes (
    id_qr       INT AUTO_INCREMENT PRIMARY KEY,
    id_batch    INT NOT NULL UNIQUE,   -- UNIQUE để đảm bảo quan hệ 1-1
    qr_value    VARCHAR(255) NOT NULL UNIQUE,
    CONSTRAINT fk_qr_batch
        FOREIGN KEY (id_batch) REFERENCES Batches(id_batch)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- INDEX bổ sung cho hiệu năng truy vấn
-- ---------------------------------------------------------------------
CREATE INDEX idx_audit_request_status ON Audit_request(status);
CREATE INDEX idx_batches_status ON Batches(audit_status);