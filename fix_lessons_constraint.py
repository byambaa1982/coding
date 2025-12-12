"""
Script to check and fix foreign key constraints.
The constraints should reference 'new_tutorials' not 'tutorials'.
"""

from app import create_app
from app.extensions import db

def fix_table_constraint(table_name):
    """Fix foreign key constraint for a table."""
    # Check current constraint
    result = db.session.execute(db.text(f"""
        SELECT 
            CONSTRAINT_NAME,
            TABLE_NAME,
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = '{table_name}'
        AND REFERENCED_TABLE_NAME IS NOT NULL
    """))
    
    constraints = result.fetchall()
    print(f"  Current foreign key constraints:")
    for constraint in constraints:
        print(f"    - {constraint[0]}: {constraint[1]}.{constraint[2]} -> {constraint[3]}.{constraint[4]}")
    
    # Check if we need to fix
    needs_fix = False
    old_constraint_name = None
    for constraint in constraints:
        if constraint[2] == 'tutorial_id' and constraint[3] == 'tutorials':
            needs_fix = True
            old_constraint_name = constraint[0]
            print(f"\n  ⚠️  Found incorrect constraint: {old_constraint_name}")
            print(f"     It references 'tutorials' but should reference 'new_tutorials'")
            break
    
    if needs_fix and old_constraint_name:
        print(f"\n  🔧 Fixing constraint...")
        
        try:
            # Drop old constraint
            print(f"     Dropping constraint: {old_constraint_name}")
            db.session.execute(db.text(f"ALTER TABLE {table_name} DROP FOREIGN KEY {old_constraint_name}"))
            
            # Add new constraint
            new_constraint_name = f"{table_name}_ibfk_new_tutorials"
            print(f"     Adding new constraint: {new_constraint_name}")
            db.session.execute(db.text(f"""
                ALTER TABLE {table_name} 
                ADD CONSTRAINT {new_constraint_name} 
                FOREIGN KEY (tutorial_id) 
                REFERENCES new_tutorials(id) 
                ON DELETE CASCADE
            """))
            
            db.session.commit()
            print(f"  ✅ Constraint fixed successfully!")
            
        except Exception as e:
            print(f"  ❌ Error fixing constraint: {str(e)}")
            db.session.rollback()
            raise
    
    elif not needs_fix:
        print(f"  ✅ Foreign key constraint is already correct!")

def main():
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("🔍 Checking foreign key constraints")
        print("="*80 + "\n")
        
        # Check both lessons and exercises tables
        tables_to_check = ['lessons', 'exercises']
        
        for table_name in tables_to_check:
            print(f"\n📋 Checking '{table_name}' table...")
            fix_table_constraint(table_name)
        
        print("\n" + "="*80)


if __name__ == '__main__':
    main()
