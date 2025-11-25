from extensions import db
from app import create_app
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("=== Checking pagos table ID sequence ===\n")
    
    # Get the current max ID in the table
    result = db.session.execute(db.text("SELECT MAX(id) FROM pagos"))
    max_id = result.scalar()
    print(f"Max ID in table: {max_id}")
    
    # Get the current sequence value
    result = db.session.execute(db.text("SELECT last_value FROM pagos_id_seq"))
    seq_value = result.scalar()
    print(f"Current sequence value: {seq_value}")
    
    if max_id and seq_value and max_id >= seq_value:
        print(f"\n⚠️  Sequence is behind! Resetting to {max_id + 1}...")
        db.session.execute(db.text(f"SELECT setval('pagos_id_seq', {max_id + 1}, false)"))
        db.session.commit()
        
        # Verify
        result = db.session.execute(db.text("SELECT last_value FROM pagos_id_seq"))
        new_seq_value = result.scalar()
        print(f"✓ Sequence reset to: {new_seq_value}")
    else:
        print("\n✓ Sequence is OK")
