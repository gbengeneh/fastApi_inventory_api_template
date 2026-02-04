import PyInstaller.__main__
import os
import sys

# Define the path to the main FastAPI app
main_script = 'main.py'

# Get the current directory
current_dir = os.getcwd()

# PyInstaller options
options = [
    '--onefile',  # Create a single executable file
    '--console',  # Show console window for debugging (change to --windowed for production)
    '--name=inventory_backend',  # Name of the executable
    '--distpath=dist',  # Output directory
    '--workpath=build',  # Working directory
    '--specpath=build',  # Spec file directory
    '--paths=.',  # Add current directory to Python path
    # Include data files
    # '--add-data', f'{os.path.join("alembic", "versions")};alembic{os.sep}versions',
    # '--add-data', f'{os.path.join("alembic", "script.py.mako")};alembic',
    # '--add-data', f'{os.path.join("alembic", "env.py")};alembic',
    # Hidden imports for FastAPI and dependencies
    '--hidden-import=uvicorn',
    '--hidden-import=uvicorn.logging',
    '--hidden-import=uvicorn.loops',
    '--hidden-import=uvicorn.loops.auto',
    '--hidden-import=uvicorn.protocols',
    '--hidden-import=uvicorn.protocols.http',
    '--hidden-import=uvicorn.protocols.http.auto',
    '--hidden-import=uvicorn.protocols.websockets',
    '--hidden-import=uvicorn.protocols.websockets.auto',
    '--hidden-import=fastapi',
    '--hidden-import=fastapi.applications',
    '--hidden-import=fastapi.routing',
    '--hidden-import=fastapi.dependencies',
    '--hidden-import=fastapi.security',
    '--hidden-import=starlette',
    '--hidden-import=starlette.applications',
    '--hidden-import=starlette.routing',
    '--hidden-import=starlette.responses',
    '--hidden-import=starlette.requests',
    '--hidden-import=starlette.background',
    '--hidden-import=sqlalchemy',
    '--hidden-import=sqlalchemy.orm',
    '--hidden-import=sqlalchemy.ext.declarative',
    '--hidden-import=sqlalchemy.engine',
    '--hidden-import=sqlalchemy.pool',
    '--hidden-import=alembic',
    '--hidden-import=alembic.context',
    '--hidden-import=alembic.script',
    '--hidden-import=alembic.environment',
    '--hidden-import=alembic.migration',
    '--hidden-import=apscheduler',
    '--hidden-import=apscheduler.schedulers',
    '--hidden-import=apscheduler.schedulers.asyncio',
    '--hidden-import=apscheduler.triggers',
    '--hidden-import=apscheduler.triggers.interval',
    '--hidden-import=pydantic',
    '--hidden-import=pydantic.fields',
    '--hidden-import=pydantic.main',
    '--hidden-import=pydantic.validators',
    '--hidden-import=passlib',
    '--hidden-import=passlib.context',
    '--hidden-import=python-jose',
    '--hidden-import=python-jose.jwt',
    '--hidden-import=python-multipart',
    '--hidden-import=bcrypt',
    '--hidden-import=cryptography',
    '--hidden-import=psycopg2',
    '--hidden-import=psycopg2.extensions',
    '--hidden-import=sqlite3',
    '--hidden-import=requests',
    '--hidden-import=httpx',
    '--hidden-import=websockets',
    '--hidden-import=websockets.client',
    '--hidden-import=websockets.server',
    '--hidden-import=asyncio',
    '--hidden-import=concurrent.futures',
    '--hidden-import=threading',
    '--hidden-import=multiprocessing',
    '--hidden-import=queue',
    '--hidden-import=json',
    '--hidden-import=datetime',
    '--hidden-import=time',
    '--hidden-import=uuid',
    '--hidden-import=re',
    '--hidden-import=typing',
    '--hidden-import=collections',
    '--hidden-import=itertools',
    '--hidden-import=functools',
    '--hidden-import=operator',
    '--hidden-import=copy',
    '--hidden-import=pickle',
    '--hidden-import=base64',
    '--hidden-import=hashlib',
    '--hidden-import=hmac',
    '--hidden-import=secrets',
    '--hidden-import=random',
    '--hidden-import=string',
    '--hidden-import=decimal',
    '--hidden-import=fractions',
    '--hidden-import=numbers',
    '--hidden-import=math',
    '--hidden-import=cmath',
    '--hidden-import=statistics',
    '--hidden-import=zoneinfo',
    '--hidden-import=zoneinfo._common',
    '--hidden-import=zoneinfo._tzpath',
    '--hidden-import=zoneinfo._zoneinfo',
    '--hidden-import=app.database.is_online',
    main_script
]

print("Building executable with PyInstaller...")
print(f"Current directory: {current_dir}")
print(f"Main script: {main_script}")

# Run PyInstaller
PyInstaller.__main__.run(options)

print("Build completed!")
print("Executable created in 'dist' directory")
