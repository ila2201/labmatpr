workspace "АСУ Театра" "Автоматизированная система управления театром для продажи билетов" {

    model {
        # Акторы
        spectator = person "Зритель" "Пользователь, который просматривает афишу и покупает билеты на спектакли"
        administrator = person "Администратор" "Сотрудник театра, управляющий репертуаром и настройками системы"
        
        # Внешние системы
        acquiring = softwareSystem "Система эквайринга" "Обрабатывает платежные транзакции по банковским картам" "External"
        emailService = softwareSystem "Email-сервис" "Отправляет электронные билеты и уведомления" "External"
        
        # Основная система
        theaterSystem = softwareSystem "АСУ Театра" "Система управления театром и продажи билетов" {
            
            # Контейнеры
            webApp = container "Web App" "Веб-приложение для пользователей" "React, TypeScript" "Web Browser" {
                tags "WebApp"
            }
            
            apiGateway = container "API Gateway" "Точка входа для всех API запросов" "Nginx, Kong" {
                tags "Gateway"
            }
            
            api = container "Backend API" "REST API для бизнес-логики" "Java, Spring Boot" {
                tags "API"
                
                # Компоненты внутри Backend API
                ticketController = component "TicketController" "Обрабатывает HTTP-запросы на покупку и бронирование билетов" "Spring MVC REST Controller"
                
                repertoireController = component "RepertoireController" "Обрабатывает HTTP-запросы по репертуару и афише" "Spring MVC REST Controller"
                
                ticketService = component "TicketService" "Бизнес-логика работы с билетами" "Spring Service"
                
                repertoireService = component "RepertoireService" "Управляет репертуаром, спектаклями и расписанием" "Spring Service"
                
                paymentService = component "PaymentService" "Интегрируется с системой эквайринга для обработки платежей" "Spring Service"
                
                notificationService = component "NotificationService" "Отправляет уведомления через email-сервис" "Spring Service"
                
                ticketRepository = component "TicketRepository" "Доступ к данным билетов и заказов" "Spring Data JPA Repository"
                
                repertoireRepository = component "RepertoireRepository" "Доступ к данным репертуара" "Spring Data JPA Repository"
            }
            
            database = container "Database" "Хранит данные о спектаклях, билетах, пользователях" "PostgreSQL" "Database" {
                tags "Database"
            }
            
            cache = container "Cache" "Кэширует часто запрашиваемые данные" "Redis" {
                tags "Cache"
            }
        }
        
        # Связи на уровне системы (Уровень 1)
        spectator -> theaterSystem "Просматривает афишу, покупает билеты"
        administrator -> theaterSystem "Управляет репертуаром, настраивает систему"
        theaterSystem -> acquiring "Обрабатывает платежи" "HTTPS/JSON"
        theaterSystem -> emailService "Отправляет билеты и уведомления" "SMTP/API"
        
        # Связи на уровне контейнеров (Уровень 2)
        spectator -> webApp "Использует" "HTTPS"
        administrator -> webApp "Управляет" "HTTPS"
        webApp -> apiGateway "Отправляет запросы" "HTTPS/REST"
        apiGateway -> api "Маршрутизирует запросы" "HTTPS/REST"
        api -> database "Читает/записывает данные" "JDBC/SQL"
        api -> cache "Кэширует данные" "TCP/Redis Protocol"
        api -> acquiring "Проводит платежи" "HTTPS/JSON"
        api -> emailService "Отправляет email" "SMTP/API"
        
        # Связи на уровне компонентов (Уровень 3)
        apiGateway -> ticketController "Маршрутизирует запросы билетов" "HTTPS/JSON"
        apiGateway -> repertoireController "Маршрутизирует запросы афиши" "HTTPS/JSON"
        
        ticketController -> ticketService "Вызывает бизнес-логику"
        repertoireController -> repertoireService "Вызывает бизнес-логику"
        
        ticketService -> paymentService "Инициирует оплату"
        ticketService -> notificationService "Отправляет уведомление о билете"
        ticketService -> ticketRepository "Сохраняет/получает билеты"
        
        repertoireService -> repertoireRepository "Получает данные репертуара"
        repertoireService -> cache "Кэширует афишу"
        
        ticketRepository -> database "Выполняет SQL-запросы" "JDBC"
        repertoireRepository -> database "Выполняет SQL-запросы" "JDBC"
        
        paymentService -> acquiring "Проводит транзакцию" "HTTPS/JSON"
        notificationService -> emailService "Отправляет email" "SMTP"
        
        # Связи на уровне кода (Уровень 4) - можно добавить классы внутри компонентов
        ticketService -> ticketController "Возвращает результат"
        repertoireService -> repertoireController "Возвращает данные"
    }

    views {
        # Уровень 1: System Context диаграмма
        systemContext theaterSystem "Level1_SystemContext" {
            include *
            autoLayout
            description "Уровень 1: Системная контекстная диаграмма АСУ Театра"
        }
        
        # Уровень 2: Container диаграмма (общая)
        container theaterSystem "Level2_Containers" {
            include *
            autoLayout
            description "Уровень 2: Диаграмма контейнеров системы АСУ Театра"
        }
        
        # Уровень 2: Container диаграмма (фокус на серверной части)
        container theaterSystem "Level2_ServerContainers" {
            include spectator administrator
            include apiGateway api database cache
            include acquiring emailService
            autoLayout
            description "Уровень 2: Диаграмма контейнеров серверного API"
        }
        
        # Уровень 3: Component диаграмма для Backend API
        component api "Level3_BackendComponents" {
            include *
            autoLayout
            description "Уровень 3: Диаграмма компонентов Backend API"
        }
        
        # Уровень 4: Code диаграмма (опционально, требует детализации классов)
        # Для Уровня 4 обычно используются UML Class diagrams в отдельных инструментах
        
        # Стили
        styles {
            element "Person" {
                shape Person
                background #08427b
                color #ffffff
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "External" {
                background #999999
                color #ffffff
            }
            element "WebApp" {
                shape WebBrowser
                background #438dd5
                color #ffffff
            }
            element "Gateway" {
                shape Pipe
                background #2e7d32
                color #ffffff
            }
            element "API" {
                shape Hexagon
                background #438dd5
                color #ffffff
            }
            element "Database" {
                shape Cylinder
                background #438dd5
                color #ffffff
            }
            element "Cache" {
                shape Cylinder
                background #ff9800
                color #ffffff
            }
            element "Component" {
                background #85bbf0
                color #000000
            }
            relationship "Relationship" {
                thickness 2
                fontSize 24
            }
        }
    }
    
}