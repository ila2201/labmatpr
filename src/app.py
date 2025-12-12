from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from typing import List, Dict, Optional
import uuid

app = Flask(__name__)
CORS(app)

# Имитация базы данных
plays_db = [
    {
        "id": 1,
        "title": "Гамлет",
        "date": "2025-12-20T19:00:00Z",
        "duration": 180,
        "genre": "трагедия",
        "description": "Классическая трагедия Уильяма Шекспира",
        "hall": "Большой зал",
        "availableSeats": 45
    },
    {
        "id": 2,
        "title": "Ревизор",
        "date": "2025-12-22T18:30:00Z",
        "duration": 150,
        "genre": "комедия",
        "description": "Комедия Николая Гоголя",
        "hall": "Малый зал",
        "availableSeats": 12
    },
    {
        "id": 3,
        "title": "Вишнёвый сад",
        "date": "2025-12-25T19:30:00Z",
        "duration": 165,
        "genre": "драма",
        "description": "Пьеса Антона Чехова",
        "hall": "Большой зал",
        "availableSeats": 78
    }
]

tickets_db = []
occupied_seats = {}  # {play_id: [(row, seat), ...]}


def validate_email(email: str) -> bool:
    """Простая валидация email"""
    return '@' in email and '.' in email.split('@')[1]


def is_seat_available(play_id: int, row: int, seat: int) -> bool:
    """Проверка доступности места"""
    if play_id not in occupied_seats:
        occupied_seats[play_id] = []
    return (row, seat) not in occupied_seats[play_id]


def find_play_by_id(play_id: int) -> Optional[Dict]:
    """Поиск спектакля по ID"""
    for play in plays_db:
        if play['id'] == play_id:
            return play
    return None


@app.route('/v1/plays', methods=['GET'])
def get_plays():
    """
    GET /plays - Получить список спектаклей
    Query параметры:
    - date: фильтр по дате (YYYY-MM-DD)
    - genre: фильтр по жанру
    """
    try:
        date_filter = request.args.get('date')
        genre_filter = request.args.get('genre')
        
        filtered_plays = plays_db.copy()
        
        # Фильтрация по дате
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                filtered_plays = [
                    play for play in filtered_plays
                    if datetime.fromisoformat(play['date'].replace('Z', '+00:00')).date() == filter_date
                ]
            except ValueError:
                return jsonify({
                    "error": "Bad Request",
                    "message": "Неверный формат даты. Используйте YYYY-MM-DD",
                    "code": "INVALID_DATE_FORMAT"
                }), 400
        
        # Фильтрация по жанру
        if genre_filter:
            filtered_plays = [
                play for play in filtered_plays
                if play['genre'].lower() == genre_filter.lower()
            ]
        
        return jsonify({"plays": filtered_plays}), 200
        
    except Exception as e:
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e),
            "code": "INTERNAL_ERROR"
        }), 500


@app.route('/v1/tickets', methods=['POST'])
def purchase_ticket():
    """
    POST /tickets - Купить билет
    Body параметры:
    - playId: ID спектакля
    - row: номер ряда
    - seat: номер места
    - userEmail: email покупателя
    - paymentMethod: способ оплаты (card, cash, certificate)
    """
    try:
        data = request.get_json()
        
        # Валидация обязательных полей
        required_fields = ['playId', 'row', 'seat', 'userEmail']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": "Bad Request",
                    "message": f"Отсутствует обязательное поле: {field}",
                    "code": "MISSING_FIELD"
                }), 400
        
        play_id = data['playId']
        row = data['row']
        seat = data['seat']
        user_email = data['userEmail']
        payment_method = data.get('paymentMethod', 'card')
        
        # Валидация email
        if not validate_email(user_email):
            return jsonify({
                "error": "Bad Request",
                "message": "Неверный формат email",
                "code": "INVALID_EMAIL"
            }), 400
        
        # Валидация номеров ряда и места
        if row < 1 or seat < 1:
            return jsonify({
                "error": "Bad Request",
                "message": "Номер ряда и места должны быть больше 0",
                "code": "INVALID_SEAT_NUMBER"
            }), 400
        
        # Проверка существования спектакля
        play = find_play_by_id(play_id)
        if not play:
            return jsonify({
                "error": "Not Found",
                "message": f"Спектакль с ID {play_id} не найден",
                "code": "PLAY_NOT_FOUND"
            }), 404
        
        # Проверка доступности места
        if not is_seat_available(play_id, row, seat):
            return jsonify({
                "error": "Bad Request",
                "message": "Место уже занято",
                "code": "SEAT_TAKEN"
            }), 400
        
        # Имитация проверки оплаты (10% шанс отказа для демонстрации)
        import random
        if payment_method == 'card' and random.random() < 0.1:
            return jsonify({
                "error": "Payment Required",
                "message": "Недостаточно средств на карте",
                "code": "PAYMENT_DECLINED"
            }), 402
        
        # Создание билета
        ticket_id = len(tickets_db) + 1
        price = 1500.00 if play['hall'] == "Большой зал" else 1000.00
        
        ticket = {
            "ticketId": ticket_id,
            "playId": play_id,
            "playTitle": play['title'],
            "row": row,
            "seat": seat,
            "price": price,
            "status": "SOLD",
            "purchaseDate": datetime.now().isoformat() + "Z",
            "userEmail": user_email,
            "qrCode": f"https://api.theater.example.com/tickets/{ticket_id}/qr"
        }
        
        # Сохранение билета
        tickets_db.append(ticket)
        if play_id not in occupied_seats:
            occupied_seats[play_id] = []
        occupied_seats[play_id].append((row, seat))
        
        # Обновление количества доступных мест
        play['availableSeats'] -= 1
        
        return jsonify(ticket), 201
        
    except Exception as e:
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e),
            "code": "INTERNAL_ERROR"
        }), 500


@app.route('/v1/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id: int):
    """
    GET /tickets/{ticket_id} - Получить информацию о билете (бонусный эндпоинт)
    """
    ticket = next((t for t in tickets_db if t['ticketId'] == ticket_id), None)
    if not ticket:
        return jsonify({
            "error": "Not Found",
            "message": f"Билет с ID {ticket_id} не найден",
            "code": "TICKET_NOT_FOUND"
        }), 404
    return jsonify(ticket), 200


@app.route('/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": "Эндпоинт не найден",
        "code": "ENDPOINT_NOT_FOUND"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Method Not Allowed",
        "message": "Метод не поддерживается для этого эндпоинта",
        "code": "METHOD_NOT_ALLOWED"
    }), 405


if __name__ == '__main__':
    print("🎭 АСУ Театра API запущена")
    print("📍 Доступные эндпоинты:")
    print("   GET  /v1/plays - Список спектаклей")
    print("   POST /v1/tickets - Покупка билета")
    print("   GET  /v1/tickets/<id> - Информация о билете")
    print("   GET  /v1/health - Health check")
    print("\n🚀 Сервер запущен на http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
