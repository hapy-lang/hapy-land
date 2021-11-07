from datetime import datetime
from fastapi import FastAPI, status, HTTPException, Response, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional

# Hapy imports
from hapy.transpiler import transpile
from hapy.exector import run as run_python


# Local  imports aka imports from the lib.
from .database import SessionLocal
from .models import BiteBase, Challenge, User as UserModel
from .pydantic_models import Request, User, RequestResponse


api = FastAPI()

# Create
# Retrieve
# Update
# Delete CRUD

db = SessionLocal()


@api.get("/challenges")
def index(limit: int = 10):
    # Fetch all bites from the data store.
    fetch_all = db.query(Challenge).limit(limit).all()
    return {"data": fetch_all}


@api.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(new_user: User):
    """A Post request to send new user data and write it to a data store."""
    username = new_user.username
    timestamp = datetime.now()
    email = new_user.email
    # Hash the password
    password = new_user.password
    register = UserModel(
        username=username, timestamp=timestamp, password=password, email=email
    )

    # Verify That this user does not exist
    db_user = (
        db.query(UserModel).filter(UserModel.username == new_user.username).count()
    )
    if db_user > 0:
        raise HTTPException(status_code=400, detail="User already exists")

    db.add(register)
    db.commit()
    db.refresh(register)
    # return register
    return {
        "data": {"username": new_user.username},
        "status": "success",
        "message": "Successfully created new user.",
    }


@api.post("/login/", response_model=RequestResponse)
def login_user(user: User, response: Response):
    """Authenticate user by sending user credentials"""
    get_user = db.query(UserModel).filter(UserModel.username == user.username)
    if get_user.count() == 1:
        # Set Cookie
        response.set_cookie(key=get_user.first().username, value="random")
        print(f"\n\n\n\n{response}\n\n\n\n")
        return {
            "data": {"user": get_user.first().username},
            "message": "Successfully returned user",
            "status": "success",
        }
    elif get_user.count() > 1:
        # This should not be the case. However, get ready yo log an issue
        pass
    else:
        return {
            "data": {"user": None},
            "message": "User does not exist",
            "status": "failed",
        }


def execute(req):
    translated = None
    python_result = None
    try:
        if req.code:
            code_in_python = transpile(req.code)
            result = "No output"
            error = ""
            # if compile only is true
            if not req.compile_only:
                result = run_python(code_in_python, return_output=True, cloud=True)
                python_result = result[1] if result[1] else result[0]
                error = result[0]
            translated = code_in_python


            return {
                "data": {
                    "python_result": python_result,
                    "python_source": translated,
                    "error": error
                },
                "status": "success" if (python_result or translated) else "error",
                "message": "Hapy output" if not error else "Error while compiling Hapy!",
            }
        return {
            "data": {"python_result": None, "python_source": None},
            "status": "error",
            "message": "Invalid code/ or file",
        }
    except Exception as e:
        return {
            "data": {"error": str(e)},
            "status": "error",
            "message": "Error while compiling Hapy",
        }




@api.post("/run", response_model=RequestResponse, status_code=status.HTTP_200_OK)
def run(item: Request):
    """Execute code, transpile code, execute and transpile"""
    if item.code:
        return execute(req=item)
    else:
        return {
            "data": {"python_result": None, "python_source": None},
            "status": "error",
            "message": "Invalid code/ or file",
        }


@api.post("/run_file/")
async def create_upload_file(file: UploadFile = File(...), option: str = Form(...)):

    content = await file.read()
    content = content.decode("utf-8")
    return execute(content, option=option)
