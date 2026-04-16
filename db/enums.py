import enum

class CategoryEnum(str, enum.Enum):
	groceries = "Groceries"
	leisure = "Leisure"
	electronics = "Electronics"
	utilities = "Utilities"
	clothing = "Clothing"
	health = "Health"
	others = "Others"
	
	
class ExpenseTypeEnum(str, enum.Enum):
	credited = "Credited"
	debited = "Debited"