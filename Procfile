# web: sh -c "cd backend && gunicorn app:app --bind 0.0.0.0:$PORT" &
# web: npm run build && npm start
# web: python app.py
# web: sh -c "cd backend && gunicorn app:app --bind 0.0.0.0:5000 & cd frontend && npm run build && npm start"
web: gunicorn app:app
