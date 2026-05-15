-- 02_seed.sql
USE cafe_order_db;
SET NAMES utf8mb4;

INSERT INTO customers (id, name, email, phone, joined_at) VALUES
(1, '김하늘', 'haneul.kim@example.com', '010-1000-0001', '2026-01-03'),
(2, '박민준', 'minjun.park@example.com', '010-1000-0002', '2026-01-12'),
(3, '이서연', 'seoyeon.lee@example.com', '010-1000-0003', '2026-02-01'),
(4, '정도윤', 'doyoon.jung@example.com', '010-1000-0004', '2026-02-08'),
(5, '최지우', 'jiwoo.choi@example.com', '010-1000-0005', '2026-02-14'),
(6, '한지민', 'jimin.han@example.com', '010-1000-0006', '2026-03-01'),
(7, '오현우', 'hyunwoo.oh@example.com', '010-1000-0007', '2026-03-09'),
(8, '윤아린', 'arin.yoon@example.com', '010-1000-0008', '2026-03-18'),
(9, '강서준', 'seojun.kang@example.com', '010-1000-0009', '2026-04-01'),
(10, '최유진', 'yujin.choi@example.com', '010-1000-0010', '2026-04-11');

INSERT INTO categories (id, name) VALUES
(1, 'Coffee'),
(2, 'Non-Coffee'),
(3, 'Tea'),
(4, 'Ade'),
(5, 'Smoothie'),
(6, 'Dessert'),
(7, 'Bakery'),
(8, 'Seasonal'),
(9, 'Beans'),
(10, 'MD');

INSERT INTO menu_items (id, category_id, name, price, is_active) VALUES
(1, 1, 'Americano', 4500.00, 1),
(2, 1, 'Cafe Latte', 5000.00, 1),
(3, 1, 'Vanilla Latte', 5500.00, 1),
(4, 1, 'Cold Brew', 5200.00, 1),
(5, 2, 'Chocolate Latte', 5500.00, 1),
(6, 3, 'Earl Grey Tea', 4800.00, 1),
(7, 3, 'Green Tea', 4800.00, 1),
(8, 4, 'Lemon Ade', 5800.00, 1),
(9, 5, 'Mango Smoothie', 6500.00, 1),
(10, 6, 'Basque Cheesecake', 6200.00, 1),
(11, 7, 'Croissant', 4200.00, 1),
(12, 8, 'Strawberry Latte', 6200.00, 1);

INSERT INTO orders (id, customer_id, order_date, status) VALUES
(1, 1, '2026-05-01 09:10:00', 'COMPLETED'),
(2, 2, '2026-05-01 10:15:00', 'COMPLETED'),
(3, 1, '2026-05-02 14:20:00', 'PAID'),
(4, 3, '2026-05-03 08:40:00', 'COMPLETED'),
(5, 4, '2026-05-03 11:25:00', 'CANCELLED'),
(6, 5, '2026-05-04 15:10:00', 'READY'),
(7, 6, '2026-05-05 13:30:00', 'COMPLETED'),
(8, 7, '2026-05-06 09:50:00', 'COMPLETED'),
(9, 8, '2026-05-07 18:05:00', 'PAID'),
(10, 9, '2026-05-08 12:00:00', 'COMPLETED'),
(11, 2, '2026-05-09 17:45:00', 'COMPLETED'),
(12, 3, '2026-05-10 10:05:00', 'COMPLETED');

INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES
(1, 1, 1, 2, 4500.00),
(2, 1, 11, 1, 4200.00),
(3, 2, 2, 1, 5000.00),
(4, 2, 10, 2, 6200.00),
(5, 3, 4, 1, 5200.00),
(6, 3, 8, 1, 5800.00),
(7, 4, 3, 2, 5500.00),
(8, 5, 9, 1, 6500.00),
(9, 6, 6, 1, 4800.00),
(10, 6, 7, 1, 4800.00),
(11, 7, 1, 1, 4500.00),
(12, 7, 10, 1, 6200.00),
(13, 8, 12, 2, 6200.00),
(14, 9, 5, 1, 5500.00),
(15, 9, 11, 2, 4200.00),
(16, 10, 2, 2, 5000.00),
(17, 11, 8, 3, 5800.00),
(18, 12, 1, 1, 4500.00),
(19, 12, 3, 1, 5500.00),
(20, 12, 10, 1, 6200.00);