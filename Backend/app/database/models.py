from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class RoleName(str, Enum):
    ADMIN = "ADMIN"
    FARMER = "FARMER"
    AUDITOR = "AUDITOR"
    PUBLIC = "PUBLIC"


class BatchStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    AUDITED = "AUDITED"
    REJECTED = "REJECTED"


class AuditDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    batches = relationship("Batch", back_populates="farmer")
    audits = relationship("Audit", back_populates="auditor")
    audit_logs = relationship("AuditLog", back_populates="user")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(SQLEnum(RoleName), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    users = relationship("User", back_populates="role")
    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan"
    )


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)

    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan"
    )


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_code = Column(String(100), unique=True, nullable=False, index=True)
    product_name = Column(String(150), nullable=False)
    crop_type = Column(String(100), nullable=True)
    quantity = Column(String(50), nullable=True)
    origin = Column(String(255), nullable=True)
    production_date = Column(DateTime, nullable=True)
    harvest_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)

    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(
        SQLEnum(BatchStatus),
        default=BatchStatus.UNVERIFIED,
        nullable=False,
        index=True
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    farmer = relationship("User", back_populates="batches")
    samples = relationship(
        "Sample",
        back_populates="batch",
        cascade="all, delete-orphan"
    )
    audits = relationship(
        "Audit",
        back_populates="batch",
        cascade="all, delete-orphan"
    )
    packages = relationship(
        "Package",
        back_populates="batch",
        cascade="all, delete-orphan"
    )
    qr_codes = relationship(
        "QRCode",
        back_populates="batch",
        cascade="all, delete-orphan"
    )


class Sample(Base):
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True)
    sample_code = Column(String(100), unique=True, nullable=False, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    sample_type = Column(String(100), nullable=True)
    collected_at = Column(DateTime, nullable=True)
    sent_to_lab_at = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    batch = relationship("Batch", back_populates="samples")
    reports = relationship(
        "LaboratoryTestReport",
        back_populates="sample",
        cascade="all, delete-orphan"
    )


class LaboratoryTestReport(Base):
    __tablename__ = "laboratory_test_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_code = Column(String(100), unique=True, nullable=False, index=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)

    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    sha256_hash = Column(String(64), nullable=True, index=True)
    test_result = Column(String(100), nullable=True)
    issued_at = Column(DateTime, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)

    sample = relationship("Sample", back_populates="reports")
    batch = relationship("Batch")


class Audit(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    auditor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    decision = Column(SQLEnum(AuditDecision), nullable=True)
    comment = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    batch = relationship("Batch", back_populates="audits")
    auditor = relationship("User", back_populates="audits")


class ProofOfIntegrity(Base):
    __tablename__ = "proofs_of_integrity"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True)
    report_id = Column(Integer, ForeignKey("laboratory_test_reports.id"), nullable=False)
    report_hash = Column(String(64), nullable=False)
    previous_hash = Column(String(64), nullable=True)
    chain_hash = Column(String(64), nullable=False, index=True)
    verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    batch = relationship("Batch")
    report = relationship("LaboratoryTestReport")


class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    package_code = Column(String(100), unique=True, nullable=False, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    trace_id = Column(String(100), unique=True, nullable=False, index=True)
    package_type = Column(String(100), nullable=True)
    quantity = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    batch = relationship("Batch", back_populates="packages")
    qr_codes = relationship(
        "QRCode",
        back_populates="package",
        cascade="all, delete-orphan"
    )


class QRCode(Base):
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True)
    qr_code_value = Column(String(255), unique=True, nullable=False, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=True)
    public_url = Column(String(500), nullable=False)
    image_path = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    activated_at = Column(DateTime, nullable=True)

    batch = relationship("Batch", back_populates="qr_codes")
    package = relationship("Package", back_populates="qr_codes")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="audit_logs")
