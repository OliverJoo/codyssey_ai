/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.2-MariaDB, for debian-linux-gnu (aarch64)
--
-- Host: localhost    Database: cafe_order_db
-- ------------------------------------------------------
-- Server version	11.8.2-MariaDB-ubu2404

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_categories_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `categories` VALUES
(4,'Ade'),
(7,'Bakery'),
(9,'Beans'),
(1,'Coffee'),
(6,'Dessert'),
(10,'MD'),
(2,'Non-Coffee'),
(8,'Seasonal'),
(5,'Smoothie'),
(3,'Tea');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `email` varchar(120) NOT NULL,
  `phone` varchar(30) DEFAULT NULL,
  `joined_at` date NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_customers_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `customers` VALUES
(1,'김하늘','haneul.kim@example.com','010-1000-0001','2026-01-03'),
(2,'박민준','minjun.park@example.com','010-1000-0002','2026-01-12'),
(3,'이서연','seoyeon.lee@example.com','010-1000-0003','2026-02-01'),
(4,'정도윤','doyoon.jung@example.com','010-1000-0004','2026-02-08'),
(5,'최지우','jiwoo.choi@example.com','010-1000-0005','2026-02-14'),
(6,'한지민','jimin.han@example.com','010-1000-0006','2026-03-01'),
(7,'오현우','hyunwoo.oh@example.com','010-1000-0007','2026-03-09'),
(8,'윤아린','arin.yoon@example.com','010-1000-0008','2026-03-18'),
(9,'강서준','seojun.kang@example.com','010-1000-0009','2026-04-01'),
(10,'최유진','yujin.choi@example.com','010-1000-0010','2026-04-11'),
(999,'테스트고객','test999@example.com','010-9999-9999','2026-05-20');
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `menu_items`
--

DROP TABLE IF EXISTS `menu_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category_id` int(11) NOT NULL,
  `name` varchar(80) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_menu_items_name` (`name`),
  KEY `fk_menu_items_category` (`category_id`),
  CONSTRAINT `fk_menu_items_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`),
  CONSTRAINT `chk_menu_items_price` CHECK (`price` > 0),
  CONSTRAINT `chk_menu_items_is_active` CHECK (`is_active` in (0,1))
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_items`
--

LOCK TABLES `menu_items` WRITE;
/*!40000 ALTER TABLE `menu_items` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `menu_items` VALUES
(1,1,'Americano',4500.00,1),
(2,1,'Cafe Latte',5000.00,1),
(3,1,'Vanilla Latte',5500.00,1),
(4,1,'Cold Brew',5200.00,1),
(5,2,'Chocolate Latte',5500.00,1),
(6,3,'Earl Grey Tea',4800.00,1),
(7,3,'Green Tea',4800.00,1),
(8,4,'Lemon Ade',5800.00,1),
(9,5,'Mango Smoothie',6500.00,1),
(10,6,'Basque Cheesecake',6200.00,1),
(11,7,'Croissant',4200.00,1),
(12,8,'Strawberry Latte',6200.00,1);
/*!40000 ALTER TABLE `menu_items` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `menu_item_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_order_items_order` (`order_id`),
  KEY `fk_order_items_menu_item` (`menu_item_id`),
  CONSTRAINT `fk_order_items_menu_item` FOREIGN KEY (`menu_item_id`) REFERENCES `menu_items` (`id`),
  CONSTRAINT `fk_order_items_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_order_items_quantity` CHECK (`quantity` > 0),
  CONSTRAINT `chk_order_items_unit_price` CHECK (`unit_price` > 0)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `order_items` VALUES
(1,1,1,2,4500.00),
(2,1,11,1,4200.00),
(3,2,2,1,5000.00),
(4,2,10,2,6200.00),
(5,3,4,1,5200.00),
(6,3,8,1,5800.00),
(7,4,3,2,5500.00),
(8,5,9,1,6500.00),
(9,6,6,1,4800.00),
(10,6,7,1,4800.00),
(11,7,1,1,4500.00),
(12,7,10,1,6200.00),
(13,8,12,2,6200.00),
(14,9,5,1,5500.00),
(15,9,11,2,4200.00),
(16,10,2,2,5000.00),
(17,11,8,3,5800.00),
(18,12,1,1,4500.00),
(19,12,3,1,5500.00),
(20,12,10,1,6200.00);
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `customer_id` int(11) NOT NULL,
  `order_date` datetime NOT NULL,
  `status` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_orders_customer_date` (`customer_id`,`order_date`),
  CONSTRAINT `fk_orders_customer` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `chk_orders_status` CHECK (`status` in ('PAID','READY','COMPLETED','CANCELLED'))
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `orders` VALUES
(1,1,'2026-05-01 09:10:00','COMPLETED'),
(2,2,'2026-05-01 10:15:00','COMPLETED'),
(3,1,'2026-05-02 14:20:00','PAID'),
(4,3,'2026-05-03 08:40:00','COMPLETED'),
(5,4,'2026-05-03 11:25:00','CANCELLED'),
(6,5,'2026-05-04 15:10:00','READY'),
(7,6,'2026-05-05 13:30:00','COMPLETED'),
(8,7,'2026-05-06 09:50:00','COMPLETED'),
(9,8,'2026-05-07 18:05:00','PAID'),
(10,9,'2026-05-08 12:00:00','COMPLETED'),
(11,2,'2026-05-09 17:45:00','COMPLETED'),
(12,3,'2026-05-10 10:05:00','COMPLETED'),
(999,999,'2026-05-20 10:00:00','PAID');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;
commit;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-05-16 10:44:44
