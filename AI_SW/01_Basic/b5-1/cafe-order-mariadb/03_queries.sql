-- 03_queries.sql
USE cafe_order_db;
SET NAMES utf8mb4;

-- Q1. 5,500원 이상 활성 메뉴 중 비싼 메뉴 TOP 5 확인
SELECT id, name, price
FROM menu_items
WHERE is_active = 1 AND price >= 5500
ORDER BY price DESC, name ASC
LIMIT 5;

-- Q2. 2026년 3월 이후 가입 고객 확인
SELECT id, name, email, joined_at
FROM customers
WHERE joined_at >= '2026-03-01'
ORDER BY joined_at ASC;

-- Q3. 최근 완료 주문 5건 확인
SELECT id, customer_id, order_date, status
FROM orders
WHERE status = 'COMPLETED'
ORDER BY order_date DESC
LIMIT 5;

-- Q4. Latte가 들어간 메뉴 검색
SELECT id, name, price
FROM menu_items
WHERE name LIKE '%Latte%'
ORDER BY price DESC;

-- Q5. 주문 목록에 고객명을 붙여 확인: INNER JOIN
SELECT o.id AS order_id, c.name AS customer_name, o.order_date, o.status
FROM orders o
INNER JOIN customers c ON o.customer_id = c.id
ORDER BY o.order_date ASC
LIMIT 5;

-- Q6. 특정 주문의 상세 메뉴 확인: 다중 INNER JOIN
SELECT o.id AS order_id,
       c.name AS customer_name,
       m.name AS menu_name,
       oi.quantity,
       oi.unit_price,
       oi.quantity * oi.unit_price AS line_total
FROM order_items oi
INNER JOIN orders o ON oi.order_id = o.id
INNER JOIN customers c ON o.customer_id = c.id
INNER JOIN menu_items m ON oi.menu_item_id = m.id
WHERE o.id = 1
ORDER BY oi.id;

-- Q7. 고객별 주문 수 확인: LEFT JOIN
-- 주문이 없는 고객도 보여야 하므로 LEFT JOIN 사용
SELECT c.id, c.name, COUNT(o.id) AS order_count
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name
ORDER BY order_count ASC, c.id ASC;

-- Q8. Coffee/Dessert 카테고리의 메뉴 확인: INNER JOIN
SELECT cat.name AS category_name, m.name AS menu_name, m.price
FROM categories cat
INNER JOIN menu_items m ON cat.id = m.category_id
WHERE cat.name IN ('Coffee', 'Dessert')
ORDER BY cat.name, m.price DESC;

-- Q9. 주문 상태별 건수 집계: COUNT + GROUP BY
SELECT status, COUNT(*) AS order_count
FROM orders
GROUP BY status
ORDER BY order_count DESC;

-- Q10. 매출 상위 메뉴 TOP 5: SUM + GROUP BY
SELECT m.name AS menu_name,
       SUM(oi.quantity) AS sold_qty,
       SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
INNER JOIN orders o ON oi.order_id = o.id
INNER JOIN menu_items m ON oi.menu_item_id = m.id
WHERE o.status IN ('PAID', 'COMPLETED')
GROUP BY m.id, m.name
ORDER BY revenue DESC
LIMIT 5;

-- Q11. 고객별 평균 주문금액: AVG + GROUP BY + 파생 집계
SELECT c.name AS customer_name,
       COUNT(DISTINCT o.id) AS paid_order_count,
       AVG(order_total.total_amount) AS avg_order_amount
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id
INNER JOIN (
    SELECT order_id, SUM(quantity * unit_price) AS total_amount
    FROM order_items
    GROUP BY order_id
) order_total ON o.id = order_total.order_id
WHERE o.status IN ('PAID', 'COMPLETED')
GROUP BY c.id, c.name
ORDER BY avg_order_amount DESC;

-- Q12. 주문이 없는 고객 찾기: 서브쿼리 NOT EXISTS
SELECT c.id, c.name, c.email
FROM customers c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.id
)
ORDER BY c.id;

-- Q13. READY 주문을 COMPLETED로 변경: UPDATE
-- 실습 안전성을 위해 트랜잭션 후 ROLLBACK
START TRANSACTION;

UPDATE orders
SET status = 'COMPLETED'
WHERE id = 6 AND status = 'READY';

SELECT id, customer_id, order_date, status
FROM orders
WHERE id = 6;

ROLLBACK;

-- Q14. 취소 주문 삭제: DELETE
-- order_items는 ON DELETE CASCADE로 함께 삭제되는지 확인
START TRANSACTION;

DELETE FROM orders
WHERE id = 5 AND status = 'CANCELLED';

SELECT COUNT(*) AS remaining_cancelled_orders
FROM orders
WHERE status = 'CANCELLED';

SELECT COUNT(*) AS remaining_items_for_order_5
FROM order_items
WHERE order_id = 5;

ROLLBACK;

-- Q15. 고객별 주문 조회 최적화를 위한 인덱스 생성
-- 적용 이유: orders에서 customer_id 조건 검색과 order_date 정렬을 자주 수행하기 때문
CREATE INDEX idx_orders_customer_date
ON orders(customer_id, order_date);

-- MariaDB 실행 계획 확인
EXPLAIN
SELECT id, customer_id, order_date, status
FROM orders
WHERE customer_id = 1
ORDER BY order_date DESC;

SELECT id, customer_id, order_date, status
FROM orders
WHERE customer_id = 1
ORDER BY order_date DESC;

-- Q16. (보너스)같은 요구사항을 JOIN과 서브쿼리
SELECT c.name AS customer_name,
       SUM(oi.quantity * oi.unit_price) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
LEFT JOIN order_items oi ON o.id = oi.order_id
WHERE o.status IN ('PAID', 'COMPLETED')
GROUP BY c.id, c.name
ORDER BY total_spent DESC;

SELECT c.name AS customer_name,
       (
         SELECT SUM(oi.quantity * oi.unit_price)
         FROM orders o
         INNER JOIN order_items oi ON o.id = oi.order_id
         WHERE o.customer_id = c.id
           AND o.status IN ('PAID', 'COMPLETED')
       ) AS total_spent
FROM customers c
WHERE (
         SELECT COUNT(*)
         FROM orders o
         WHERE o.customer_id = c.id
           AND o.status IN ('PAID', 'COMPLETED')
      ) > 0
ORDER BY total_spent DESC;
