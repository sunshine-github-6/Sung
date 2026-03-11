# 测试models模块导入
print("Testing models import...")
try:
    from models import db, OriginTracingBranches, OriginTracingLocations, OriginTracingMigrations, User, MigrationSubmission
    print("✅ Import successful!")
    print(f"db: {db}")
    print(f"OriginTracingBranches: {OriginTracingBranches}")
    print(f"OriginTracingLocations: {OriginTracingLocations}")
    print(f"OriginTracingMigrations: {OriginTracingMigrations}")
    print(f"User: {User}")
    print(f"MigrationSubmission: {MigrationSubmission}")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()