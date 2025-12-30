# Import FastAPI to create the web server
# Depends is used for dependency injection (automatic DB session handling)
from fastapi import FastAPI, Depends

# Session is used only for type hinting (clarity)
from sqlalchemy.orm import Session

# Import database connection and session factory
from database import SessionLocal, engine

# Import database models (Ticket table)
import models

# Import lottery logic (random number generation)
from services.lottery_service import generate_ticket_numbers, draw_winning_numbers


# Create FastAPI application instance
app = FastAPI()

# Create database tables if they do NOT already exist
# This runs only once at startup
models.Base.metadata.create_all(bind=engine)


# This variable stores the winning numbers IN MEMORY
# ⚠️ This will reset if the server restarts
winning_numbers = []


# ------------------ DATABASE SESSION HANDLER ------------------
# This function provides a database session for each request
def get_db():
    # Open a new database session
    db = SessionLocal()
    try:
        # Give the session to the API endpoint
        yield db
    finally:
        # Close the session after the request finishes
        db.close()


# ------------------ BUY TICKET API ------------------
# POST request because we are CREATING data
@app.post("/buy-ticket")
def buy_ticket(user_name: str, db: Session = Depends(get_db)):
    # Generate 6 random lottery numbers
    numbers = generate_ticket_numbers()

    # Create a Ticket object (represents one DB row)
    ticket = models.Ticket(
        user_name=user_name,
        # Store numbers as a comma-separated string in DB
        numbers=",".join(map(str, numbers))
    )

    # Add ticket to DB session
    db.add(ticket)

    # Save ticket permanently in database
    db.commit()

    # Refresh ticket to get auto-generated ID
    db.refresh(ticket)

    # Send response back to client
    return {
        "ticket_id": ticket.id,
        "numbers": numbers
    }


# ------------------ DRAW LOTTERY API ------------------
# Generates winning numbers
@app.post("/draw")
def draw_lottery():
    global winning_numbers

    # Generate winning numbers
    winning_numbers = draw_winning_numbers()

    # Return winning numbers to client
    return {"winning_numbers": winning_numbers}


# ------------------ CHECK RESULT API ------------------
# ticket_id comes from URL path
@app.get("/check-result/{ticket_id}")
def check_result(ticket_id: int, db: Session = Depends(get_db)):

    # Fetch ticket from database using ticket_id
    ticket = db.query(models.Ticket)\
               .filter(models.Ticket.id == ticket_id)\
               .first()

    # If ticket does not exist, return error
    if not ticket:
        return {"error": "Ticket not found"}

    # Convert stored string numbers back into integer list
    ticket_numbers = list(map(int, ticket.numbers.split(",")))

    # Find common numbers between ticket and winning numbers
    matches = set(ticket_numbers) & set(winning_numbers)

    # Return result
    return {
        "ticket_numbers": ticket_numbers,
        "winning_numbers": winning_numbers,
        "matched_numbers": list(matches),
        "match_count": len(matches)
    }
