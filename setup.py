"""
One-time project setup. Run with: python setup.py
"""
import os, subprocess, sys

DIRS = ['api/routes', 'evaluation']
for d in DIRS:
    os.makedirs(d, exist_ok=True)
    print(f'  created  {d}/')

print('\nCreating virtual environment...')
subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)

pip = 'venv/bin/pip' if os.name != 'nt' else 'venv\\Scripts\\pip'

packages = [
    'fastapi==0.112.0',
    'uvicorn[standard]==0.30.5',
    'pydantic==2.8.2',
    'python-dotenv==1.0.1',
    'sqlalchemy==2.0.31',
    'anthropic==0.34.0',
    'httpx==0.27.0',
    'beautifulsoup4==4.12.3',
]
subprocess.run([pip, 'install'] + packages, check=True)
subprocess.run([pip, 'freeze'], stdout=open('requirements.txt', 'w'), check=True)

with open('.gitignore', 'w') as f:
    f.write('venv/\n.env\n__pycache__/\n*.pyc\n')

if not os.path.exists('.env'):
    with open('.env', 'w') as f:
        f.write('ANTHROPIC_API_KEY=your_anthropic_key_here\n')
        f.write('GOOGLE_API_KEY=your_google_api_key_here\n')
        f.write('GOOGLE_CSE_ID=your_custom_search_engine_id_here\n')
        f.write('DATABASE_URL=sqlite:///./gvsu_chatbot.db\n')
    print('\n  .env template created — fill in your API keys!')

print('\n✅  Setup complete. Activate: source venv/bin/activate')