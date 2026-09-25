/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.19-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: plpe_db
-- ------------------------------------------------------
-- Server version	10.11.19-MariaDB-ubu2204

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES
('670c77ce0ce5');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `business_categories`
--

DROP TABLE IF EXISTS `business_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `business_categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `business_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_business_category` (`business_id`,`category_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `business_categories_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE,
  CONSTRAINT `business_categories_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `business_categories`
--

LOCK TABLES `business_categories` WRITE;
/*!40000 ALTER TABLE `business_categories` DISABLE KEYS */;
INSERT INTO `business_categories` VALUES
(1,53,25),
(2,54,25);
/*!40000 ALTER TABLE `business_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `businesses`
--

DROP TABLE IF EXISTS `businesses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `businesses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `owner_id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL,
  `description` text DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `latitude` float DEFAULT NULL,
  `longitude` float DEFAULT NULL,
  `phone` varchar(30) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `logo_url` varchar(500) DEFAULT NULL,
  `status` enum('PENDING','APPROVED','SUSPENDED','DELETED') NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `owner_id` (`owner_id`),
  KEY `ix_businesses_city` (`city`),
  KEY `ix_businesses_name` (`name`),
  CONSTRAINT `businesses_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `businesses`
--

LOCK TABLES `businesses` WRITE;
/*!40000 ALTER TABLE `businesses` DISABLE KEYS */;
INSERT INTO `businesses` VALUES
(41,44,'Emprendimiento 1','Descripción del emprendimiento 1 - productos artesanales y locales',NULL,'Mar del Plata',NULL,NULL,NULL,NULL,NULL,NULL,'PENDING','2026-08-16 22:50:43','2026-09-24 22:50:43',NULL),
(42,41,'Emprendimiento 2','Descripción del emprendimiento 2 - productos artesanales y locales',NULL,'Rosario',NULL,NULL,NULL,NULL,NULL,NULL,'SUSPENDED','2026-09-22 22:50:43','2026-09-24 22:50:43',NULL),
(43,40,'Emprendimiento 3','Descripción del emprendimiento 3 - productos artesanales y locales',NULL,'Buenos Aires',NULL,NULL,NULL,NULL,NULL,NULL,'PENDING','2026-07-28 22:50:43','2026-09-24 22:50:43',NULL),
(44,43,'Emprendimiento 4','Descripción del emprendimiento 4 - productos artesanales y locales',NULL,'Mendoza',NULL,NULL,NULL,NULL,NULL,NULL,'DELETED','2026-07-05 22:50:43','2026-09-24 22:50:43',NULL),
(45,46,'Emprendimiento 5','Descripción del emprendimiento 5 - productos artesanales y locales',NULL,'Rosario',NULL,NULL,NULL,NULL,NULL,NULL,'SUSPENDED','2026-09-18 22:50:43','2026-09-24 22:50:43',NULL),
(46,44,'Emprendimiento 6','Descripción del emprendimiento 6 - productos artesanales y locales',NULL,'Mar del Plata',NULL,NULL,NULL,NULL,NULL,NULL,'DELETED','2026-09-08 22:50:43','2026-09-24 22:50:43',NULL),
(47,44,'Emprendimiento 7','Descripción del emprendimiento 7 - productos artesanales y locales',NULL,'Córdoba',NULL,NULL,NULL,NULL,NULL,NULL,'DELETED','2026-07-09 22:50:43','2026-09-24 22:50:43',NULL),
(48,42,'Emprendimiento 8','Descripción del emprendimiento 8 - productos artesanales y locales',NULL,'Mar del Plata',NULL,NULL,NULL,NULL,NULL,NULL,'PENDING','2026-08-23 22:50:43','2026-09-24 22:50:43',NULL),
(49,43,'Emprendimiento 9','Descripción del emprendimiento 9 - productos artesanales y locales',NULL,'Córdoba',NULL,NULL,NULL,NULL,NULL,NULL,'APPROVED','2026-07-03 22:50:43','2026-09-24 22:50:43',NULL),
(50,40,'Emprendimiento 10','Descripción del emprendimiento 10 - productos artesanales y locales',NULL,'Rosario',NULL,NULL,NULL,NULL,NULL,NULL,'APPROVED','2026-08-28 22:50:43','2026-09-24 22:50:43',NULL),
(51,45,'Emprendimiento 11','Descripción del emprendimiento 11 - productos artesanales y locales',NULL,'Mendoza',NULL,NULL,NULL,NULL,NULL,NULL,'APPROVED','2026-08-03 22:50:43','2026-09-24 22:50:43',NULL),
(52,41,'Emprendimiento 12','Descripción del emprendimiento 12 - productos artesanales y locales',NULL,'Mar del Plata',NULL,NULL,NULL,NULL,NULL,NULL,'PENDING','2026-09-11 22:50:43','2026-09-24 22:50:43',NULL),
(53,48,'Negocio Frontend Test','Prueba',NULL,'Cordoba',NULL,NULL,NULL,NULL,NULL,NULL,'DELETED','2026-09-24 23:03:38','2026-09-24 23:07:34','2026-09-24 23:07:34'),
(54,48,'Flow Test Biz',NULL,NULL,'Rosario',NULL,NULL,NULL,NULL,NULL,NULL,'DELETED','2026-09-24 23:10:50','2026-09-24 23:10:50','2026-09-24 23:10:50'),
(55,51,'Mi Huerta Test','de prueba',NULL,'Formosa',NULL,NULL,NULL,NULL,NULL,NULL,'PENDING','2026-09-25 02:11:15','2026-09-25 02:11:15',NULL);
/*!40000 ALTER TABLE `businesses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `icon` varchar(100) DEFAULT NULL,
  `active` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_categories_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES
(25,'Alimentos y Bebidas','Categoría de productos alimentos y bebidas',NULL,1,'2026-09-24 22:50:43'),
(26,'Artesanía','Categoría de productos artesanía',NULL,1,'2026-09-24 22:50:43'),
(27,'Ropa y Accesorios','Categoría de productos ropa y accesorios',NULL,1,'2026-09-24 22:50:43'),
(28,'Tecnología y Software','Categoría de productos tecnología y software',NULL,1,'2026-09-24 22:50:43'),
(29,'Salud y Bienestar','Categoría de productos salud y bienestar',NULL,1,'2026-09-24 22:50:43'),
(30,'Decoración y Hogar','Categoría de productos decoración y hogar',NULL,1,'2026-09-24 22:50:43');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contact_requests`
--

DROP TABLE IF EXISTS `contact_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `contact_requests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `business_id` int(11) DEFAULT NULL,
  `name` varchar(150) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(30) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `status` enum('NEW','CONTACTED','CLOSED') NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `handled_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contact_requests`
--

LOCK TABLES `contact_requests` WRITE;
/*!40000 ALTER TABLE `contact_requests` DISABLE KEYS */;
INSERT INTO `contact_requests` VALUES
(1,52,'Juan Pérez','juan@ejemplo.com','+541112345678','Quiero que me contacten por el emprendimiento.','CONTACTED','2026-09-25 01:07:14','2026-09-25 01:07:21'),
(2,52,'Visitante CDP','cdp@test.com','1122334455','Solicito ser contactado.','NEW','2026-09-25 01:13:36',NULL),
(3,52,'Visitante CDP','cdp@test.com','1122334455','Solicito ser contactado.','NEW','2026-09-25 01:13:58',NULL);
/*!40000 ALTER TABLE `contact_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `favorites`
--

DROP TABLE IF EXISTS `favorites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `favorites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `business_id` int(11) DEFAULT NULL,
  `product_id` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_favorite` (`user_id`,`business_id`,`product_id`),
  KEY `business_id` (`business_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE,
  CONSTRAINT `favorites_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `favorites_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `favorites`
--

LOCK TABLES `favorites` WRITE;
/*!40000 ALTER TABLE `favorites` DISABLE KEYS */;
INSERT INTO `favorites` VALUES
(17,43,48,NULL,'2026-09-11 22:50:43'),
(18,44,48,NULL,'2026-09-12 22:50:43'),
(19,45,48,NULL,'2026-09-01 22:50:43'),
(20,45,49,NULL,'2026-09-11 22:50:43'),
(21,41,50,NULL,'2026-08-29 22:50:43'),
(22,43,52,NULL,'2026-08-27 22:50:43'),
(23,43,52,NULL,'2026-09-12 22:50:43'),
(24,44,47,NULL,'2026-09-16 22:50:43'),
(25,42,43,NULL,'2026-09-23 22:50:43'),
(26,47,42,NULL,'2026-08-27 22:50:43'),
(27,44,52,NULL,'2026-09-09 22:50:43'),
(28,45,48,NULL,'2026-08-26 22:50:43'),
(29,44,48,NULL,'2026-08-31 22:50:43'),
(30,42,48,NULL,'2026-09-08 22:50:43'),
(31,46,50,NULL,'2026-09-05 22:50:43');
/*!40000 ALTER TABLE `favorites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inquiries`
--

DROP TABLE IF EXISTS `inquiries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `inquiries` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `business_id` int(11) NOT NULL,
  `sender_id` int(11) DEFAULT NULL,
  `sender_name` varchar(150) NOT NULL,
  `sender_email` varchar(255) NOT NULL,
  `sender_phone` varchar(30) DEFAULT NULL,
  `message` text NOT NULL,
  `status` enum('NEW','READ','ANSWERED','CLOSED') NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `responded_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `business_id` (`business_id`),
  KEY `sender_id` (`sender_id`),
  CONSTRAINT `inquiries_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE,
  CONSTRAINT `inquiries_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inquiries`
--

LOCK TABLES `inquiries` WRITE;
/*!40000 ALTER TABLE `inquiries` DISABLE KEYS */;
INSERT INTO `inquiries` VALUES
(3,52,NULL,'Visitante Anónimo','visita@ejemplo.com',NULL,'Hola, quiero consultar.','NEW','2026-09-24 23:21:45',NULL);
/*!40000 ALTER TABLE `inquiries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `password_resets`
--

DROP TABLE IF EXISTS `password_resets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `password_resets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `token_hash` varchar(255) NOT NULL,
  `expires_at` datetime NOT NULL,
  `used` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_password_resets_token_hash` (`token_hash`),
  CONSTRAINT `password_resets_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `password_resets`
--

LOCK TABLES `password_resets` WRITE;
/*!40000 ALTER TABLE `password_resets` DISABLE KEYS */;
/*!40000 ALTER TABLE `password_resets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(100) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `business_id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL,
  `description` text DEFAULT NULL,
  `price` float DEFAULT NULL,
  `currency` varchar(3) NOT NULL,
  `stock` int(11) DEFAULT NULL,
  `image_url` varchar(500) DEFAULT NULL,
  `active` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `business_id` (`business_id`),
  KEY `ix_products_name` (`name`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES
(28,45,'Producto 1','Descripción del producto 1',3684.14,'ARS',141,'https://via.placeholder.com/300x200?product=1',0,'2026-09-17 22:50:43','2026-09-24 22:50:43',NULL),
(29,48,'Producto 2','Descripción del producto 2',1499.2,'ARS',385,'https://via.placeholder.com/300x200?product=2',1,'2026-07-26 22:50:43','2026-09-24 22:50:43',NULL),
(30,42,'Producto 3','Descripción del producto 3',1167.65,'ARS',450,'https://via.placeholder.com/300x200?product=3',1,'2026-09-12 22:50:43','2026-09-24 22:50:43',NULL),
(31,43,'Producto 4','Descripción del producto 4',2053.99,'ARS',479,'https://via.placeholder.com/300x200?product=4',1,'2026-08-16 22:50:43','2026-09-24 22:50:43',NULL),
(32,49,'Producto 5','Descripción del producto 5',2357.11,'ARS',171,'https://via.placeholder.com/300x200?product=5',0,'2026-08-11 22:50:43','2026-09-24 22:50:43',NULL),
(33,42,'Producto 6','Descripción del producto 6',3400.37,'ARS',159,'https://via.placeholder.com/300x200?product=6',1,'2026-09-20 22:50:43','2026-09-24 22:50:43',NULL),
(34,41,'Producto 7','Descripción del producto 7',2209.23,'ARS',95,'https://via.placeholder.com/300x200?product=7',1,'2026-09-06 22:50:43','2026-09-24 22:50:43',NULL),
(35,50,'Producto 8','Descripción del producto 8',3217.5,'ARS',441,'https://via.placeholder.com/300x200?product=8',0,'2026-09-03 22:50:43','2026-09-24 22:50:43',NULL),
(36,48,'Producto 9','Descripción del producto 9',2506.96,'ARS',38,'https://via.placeholder.com/300x200?product=9',1,'2026-09-09 22:50:43','2026-09-24 22:50:43',NULL),
(37,49,'Producto 10','Descripción del producto 10',2667.02,'ARS',73,'https://via.placeholder.com/300x200?product=10',0,'2026-09-04 22:50:43','2026-09-24 22:50:43',NULL),
(38,48,'Producto 11','Descripción del producto 11',2815.53,'ARS',223,'https://via.placeholder.com/300x200?product=11',1,'2026-09-02 22:50:43','2026-09-24 22:50:43',NULL),
(39,48,'Producto 12','Descripción del producto 12',4911.86,'ARS',490,'https://via.placeholder.com/300x200?product=12',1,'2026-08-09 22:50:43','2026-09-24 22:50:43',NULL),
(40,49,'Producto 13','Descripción del producto 13',1891.68,'ARS',328,'https://via.placeholder.com/300x200?product=13',1,'2026-09-16 22:50:43','2026-09-24 22:50:43',NULL),
(41,45,'Producto 14','Descripción del producto 14',1061.15,'ARS',174,'https://via.placeholder.com/300x200?product=14',0,'2026-08-27 22:50:43','2026-09-24 22:50:43',NULL),
(42,51,'Producto 15','Descripción del producto 15',1276.63,'ARS',31,'https://via.placeholder.com/300x200?product=15',1,'2026-08-21 22:50:43','2026-09-24 22:50:43',NULL),
(43,41,'Producto 16','Descripción del producto 16',2835.65,'ARS',18,'https://via.placeholder.com/300x200?product=16',1,'2026-09-06 22:50:43','2026-09-24 22:50:43',NULL),
(44,43,'Producto 17','Descripción del producto 17',4267.23,'ARS',491,'https://via.placeholder.com/300x200?product=17',1,'2026-08-26 22:50:43','2026-09-24 22:50:43',NULL),
(45,49,'Producto 18','Descripción del producto 18',1762.49,'ARS',234,'https://via.placeholder.com/300x200?product=18',1,'2026-09-03 22:50:43','2026-09-24 22:50:43',NULL),
(46,50,'Producto 19','Descripción del producto 19',641.33,'ARS',23,'https://via.placeholder.com/300x200?product=19',1,'2026-08-12 22:50:43','2026-09-24 22:50:43',NULL),
(47,42,'Producto 20','Descripción del producto 20',1394.78,'ARS',152,'https://via.placeholder.com/300x200?product=20',1,'2026-07-28 22:50:43','2026-09-24 22:50:43',NULL),
(48,51,'Producto 21','Descripción del producto 21',1847.21,'ARS',133,'https://via.placeholder.com/300x200?product=21',1,'2026-09-16 22:50:43','2026-09-24 22:50:43',NULL),
(49,42,'Producto 22','Descripción del producto 22',410.02,'ARS',486,'https://via.placeholder.com/300x200?product=22',1,'2026-07-27 22:50:43','2026-09-24 22:50:43',NULL),
(50,51,'Producto 23','Descripción del producto 23',1095.94,'ARS',280,'https://via.placeholder.com/300x200?product=23',0,'2026-09-15 22:50:43','2026-09-24 22:50:43',NULL),
(51,42,'Producto 24','Descripción del producto 24',1381.99,'ARS',462,'https://via.placeholder.com/300x200?product=24',1,'2026-09-05 22:50:43','2026-09-24 22:50:43',NULL),
(52,41,'Producto 25','Descripción del producto 25',1354.66,'ARS',256,'https://via.placeholder.com/300x200?product=25',1,'2026-08-01 22:50:43','2026-09-24 22:50:43',NULL),
(53,42,'Producto Frontend',NULL,9999.99,'ARS',5,NULL,0,'2026-09-24 23:07:22','2026-09-24 23:07:23','2026-09-24 23:07:23'),
(54,55,'Tomate',NULL,500,'ARS',NULL,NULL,1,'2026-09-25 02:11:15','2026-09-25 02:11:15',NULL);
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_permissions`
--

DROP TABLE IF EXISTS `role_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `role_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_role_perm` (`role_id`,`permission_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_permissions`
--

LOCK TABLES `role_permissions` WRITE;
/*!40000 ALTER TABLE `role_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `role_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES
(1,'admin','Acceso total a la plataforma'),
(2,'producer','Productor o emprendedor'),
(3,'user','Usuario consumidor');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `services`
--

DROP TABLE IF EXISTS `services`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `services` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `business_id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL,
  `description` text DEFAULT NULL,
  `price` float DEFAULT NULL,
  `currency` varchar(3) NOT NULL,
  `duration_minutes` int(11) DEFAULT NULL,
  `image_url` varchar(500) DEFAULT NULL,
  `active` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `business_id` (`business_id`),
  KEY `ix_services_name` (`name`),
  CONSTRAINT `services_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `services`
--

LOCK TABLES `services` WRITE;
/*!40000 ALTER TABLE `services` DISABLE KEYS */;
INSERT INTO `services` VALUES
(3,42,'Servicio Frontend',NULL,7777,'ARS',60,NULL,0,'2026-09-24 23:07:22','2026-09-24 23:07:23','2026-09-24 23:07:23');
/*!40000 ALTER TABLE `services` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sessions`
--

DROP TABLE IF EXISTS `sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `sessions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `refresh_token_hash` varchar(255) NOT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` varchar(255) DEFAULT NULL,
  `expires_at` datetime NOT NULL,
  `revoked` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_sessions_refresh_token_hash` (`refresh_token_hash`),
  CONSTRAINT `sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sessions`
--

LOCK TABLES `sessions` WRITE;
/*!40000 ALTER TABLE `sessions` DISABLE KEYS */;
INSERT INTO `sessions` VALUES
(1,1,'$argon2id$v=19$m=65536,t=3,p=4$cs4ZI4Swdu59r5VSCoHwXg$RKgj0KWVbG1ym6MmD9j0iy3gud8XlOmMioK/S8gtt+4','172.25.0.1','curl/8.14.1','2026-10-01 22:12:27',0,'2026-09-24 22:12:27'),
(2,2,'$argon2id$v=19$m=65536,t=3,p=4$JuS8tzamdO6ds7a29j6ntA$gC7HpR2OS0NDgJnAxoSlvwFZ35JMRjrj731HVhp23xY','172.25.0.1','curl/8.14.1','2026-10-01 22:20:48',0,'2026-09-24 22:20:48'),
(3,3,'$argon2id$v=19$m=65536,t=3,p=4$eC9lzBnD2Pv/33uPkfK+1w$F2F266v9N4NlhYSBMz6GyaBUMe+cNntStFV5OeC8L/0','172.25.0.1','curl/8.14.1','2026-10-01 22:33:08',0,'2026-09-24 22:33:08'),
(4,4,'$argon2id$v=19$m=65536,t=3,p=4$3dub01oLQQjBGAMAYCwlZA$ntnsmJwpBoDZuH5HMCOq97mkoeE4Tfz15Gbl1re04/Q','172.25.0.1','curl/8.14.1','2026-10-01 22:37:04',0,'2026-09-24 22:37:04'),
(5,5,'$argon2id$v=19$m=65536,t=3,p=4$ac25NwZAqBVibG1NidE6pw$E2e66IKBsbfZiWmYw5LYvalS5byDEE9jJr2lc83+Yc8','172.25.0.1','curl/8.14.1','2026-10-01 22:38:12',0,'2026-09-24 22:38:12'),
(6,48,'$argon2id$v=19$m=65536,t=3,p=4$0drbW+u9txYCoPT+3/ufkw$3An4LYT/pw5dKMStcu1LqEvtoZK450dCUeAG27huNxM','172.25.0.1','curl/8.14.1','2026-10-01 23:03:12',0,'2026-09-24 23:03:12'),
(7,48,'$argon2id$v=19$m=65536,t=3,p=4$gvCeEyLE+J/zfk9pjRGCcA$j2lA7xcoP8EMFp9qFONpg/HOY482D0SKmzvV00Z29zs','172.25.0.1','curl/8.14.1','2026-10-01 23:03:17',0,'2026-09-24 23:03:17'),
(8,48,'$argon2id$v=19$m=65536,t=3,p=4$g7CWcq5VKsXY+9/bWyslRA$L1mhLgiDV2BjX/y9X6NUjoiXDImrfgSgXc6az5e7ajM','172.25.0.1','curl/8.14.1','2026-10-01 23:03:37',0,'2026-09-24 23:03:37'),
(9,48,'$argon2id$v=19$m=65536,t=3,p=4$7h0DQEhJKUWIMYbwnvO+Vw$mvgO3vzaOtlY1KSCMIkBo/DT9oucUs9X7Ers8KCaZFQ','172.25.0.1','curl/8.14.1','2026-10-01 23:07:07',0,'2026-09-24 23:07:07'),
(10,48,'$argon2id$v=19$m=65536,t=3,p=4$K2WMEYKQspYSonSOcQ5hDA$8g+VA3wN/Ba9eJ037RlW0IFxp3jaUzXRT4nMBFGPwUk','172.25.0.1','curl/8.14.1','2026-10-01 23:07:18',0,'2026-09-24 23:07:18'),
(11,48,'$argon2id$v=19$m=65536,t=3,p=4$r1XqXWsNAaB0TilFyLk3Rg$5d1EvuuLGR732ckNeEAmpUEX+j+B0fhJTZEB9S4woQM','172.25.0.1','curl/8.14.1','2026-10-01 23:07:22',0,'2026-09-24 23:07:22'),
(12,48,'$argon2id$v=19$m=65536,t=3,p=4$znlPqdX6P0fo3RujFELovQ$RWpVSSdLJHOPVHZumzcdo8y1W/AG702O3ZgtUMZCkto','172.25.0.1','curl/8.14.1','2026-10-01 23:07:34',0,'2026-09-24 23:07:34'),
(13,48,'$argon2id$v=19$m=65536,t=3,p=4$JoRw7p2T8j6HcC4F4LwXgg$jzUBJBTjyl15lubQ+6159UKqTW5xHpqskktW2giFliU','172.25.0.1','curl/8.14.1','2026-10-01 23:07:51',0,'2026-09-24 23:07:51'),
(14,48,'$argon2id$v=19$m=65536,t=3,p=4$AEDovdfa+793TinFWKt1Dg$WM8OJ4JgXIZaeyt2KzXh6MugdsY5gNth0kHP+nfIr5c','172.25.0.1','curl/8.14.1','2026-10-01 23:08:19',0,'2026-09-24 23:08:19'),
(15,48,'$argon2id$v=19$m=65536,t=3,p=4$CsE4R2hN6T2ndI5xTmnNOQ$hA099p5eGn48yspy4Ms7B5Xmcfk9zQCMtE570WbZir0','172.25.0.1','curl/8.14.1','2026-10-01 23:09:48',0,'2026-09-24 23:09:48'),
(16,48,'$argon2id$v=19$m=65536,t=3,p=4$gnDOmfPeGyPk3Lu3dk4phQ$xXBoAipVPeZebibB5dDarWmoFu8ym9ktN9YOR+vmXjw','172.25.0.1','curl/8.14.1','2026-10-01 23:10:49',0,'2026-09-24 23:10:49'),
(17,48,'$argon2id$v=19$m=65536,t=3,p=4$qhWitDYmxBjD2JszxliL0Q$YDEIYOGPHoQrM2lgptTqFksZpTEM86ZANdLlH3CqrMU','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36','2026-10-01 23:11:58',0,'2026-09-24 23:11:58'),
(18,48,'$argon2id$v=19$m=65536,t=3,p=4$FgIAAICQUmoNAaD0PscYow$J3BZrrbWl53EkPPi7O2yjKfZlc7Qv8fVEL7QQ7K643I','172.25.0.1','curl/8.14.1','2026-10-01 23:20:58',0,'2026-09-24 23:20:58'),
(19,48,'$argon2id$v=19$m=65536,t=3,p=4$dI4RAoDwHoMw5pyT8r6Xkg$gpTPd+9ckBIqVPwwlAwcyVQtr+ICC8XWcXOwG3kB0DM','172.25.0.1','curl/8.14.1','2026-10-01 23:21:45',0,'2026-09-24 23:21:45'),
(20,48,'$argon2id$v=19$m=65536,t=3,p=4$kpISopSS0novhZByDsF47w$79sDWAYvtMK0AbaOGE5G7oxpP6Iscdr1o3srWp/Pics','172.25.0.1','curl/8.14.1','2026-10-02 01:07:21',0,'2026-09-25 01:07:21'),
(21,48,'$argon2id$v=19$m=65536,t=3,p=4$5Nz7XyslZAzB+H9vjVHqnQ$Dz+u4pfQ9q97z2PT3jb/sjmeonntosjbaazRUZ/gBkc','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/153.0.0.0 Safari/537.36','2026-10-02 01:14:00',0,'2026-09-25 01:14:00'),
(22,48,'$argon2id$v=19$m=65536,t=3,p=4$fS+lFIIQwtibc67VmpOyVg$8ThCLXZ3EKeXZZk4uAD7TuyyeMbiKPBw+ws/JrP4tnY','172.25.0.1','curl/8.14.1','2026-10-02 01:14:21',0,'2026-09-25 01:14:21'),
(23,48,'$argon2id$v=19$m=65536,t=3,p=4$8P6fs9ba27v3/v9fa43xng$+z9z0SKvUVbh1HSb6co1R5iFOhlgGDe/eotwQXViE90','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/153.0.0.0 Safari/537.36','2026-10-02 01:20:56',0,'2026-09-25 01:20:56'),
(24,48,'$argon2id$v=19$m=65536,t=3,p=4$DyEkhLBWypnz/j9HKMVYCw$+Xuckl+GgpqgLXjPo5oiL2plelytvH6cikNZJNVcc+s','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/153.0.0.0 Safari/537.36','2026-10-02 01:25:31',0,'2026-09-25 01:25:31'),
(25,48,'$argon2id$v=19$m=65536,t=3,p=4$KwWAUGpNKeWcE+J8T8mZ0w$Lpupdkzthkq/8Rh9L3XI614cYQKojeR1WQe/xA0AGQM','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/153.0.0.0 Safari/537.36','2026-10-02 01:26:12',0,'2026-09-25 01:26:12'),
(26,48,'$argon2id$v=19$m=65536,t=3,p=4$fG/NuTemlPJ+r1XKGQPgHA$8+SqMHo8qsO2nkXdIMmJhjriaIaSVu0fa3g1FPjPG68','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36','2026-10-02 01:51:58',0,'2026-09-25 01:51:58'),
(27,48,'$argon2id$v=19$m=65536,t=3,p=4$cs75H4MwpnQOIWTMGUMIwQ$9iVW2UuG+bw0i52ESQ9kxICq1YZFsVqeKir/tBiTxkQ','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/153.0.0.0 Safari/537.36','2026-10-02 01:55:36',0,'2026-09-25 01:55:36'),
(28,48,'$argon2id$v=19$m=65536,t=3,p=4$610r5by3tjZGyDknxHjv3Q$gNCAPfCh3o21Ch5O8sjAUHujY9NaPmQ+8XsSEXXDUgs','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/153.0.0.0 Safari/537.36','2026-10-02 01:58:32',0,'2026-09-25 01:58:32'),
(29,48,'$argon2id$v=19$m=65536,t=3,p=4$bk0J4TwHYAwhxHgvhbAWQg$fx0ZgcLjl/Y/Dx6jIOvyIq9EE9sYlRoURykdAJ2MF94','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/153.0.0.0 Safari/537.36','2026-10-02 01:58:52',0,'2026-09-25 01:58:52'),
(30,49,'$argon2id$v=19$m=65536,t=3,p=4$7z3n/H/vnRMCQMg5B0Bo7Q$0plNxxA7Ax8i7+Y0rVJl/++nwimiAC6amT6EHLheFyY','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36','2026-10-02 02:02:02',0,'2026-09-25 02:02:02'),
(31,48,'$argon2id$v=19$m=65536,t=3,p=4$OQcghND6/3/vXUsJ4XyPsQ$gJIfAbZALGlbpWgcxa8tl0lu4VZ04o5qOBitEDvLBNE','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/153.0.0.0 Safari/537.36','2026-10-02 02:04:28',0,'2026-09-25 02:04:28'),
(32,50,'$argon2id$v=19$m=65536,t=3,p=4$oxTCOGcsxVhLCeEcA4DQ+g$acuDi6hDS+BPqvRxLJZcJ48cpExkR77J+hNc16TyU8o','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36','2026-10-02 02:06:46',0,'2026-09-25 02:06:46'),
(33,51,'$argon2id$v=19$m=65536,t=3,p=4$DKEUQqg1RggBoJSS0jrHGA$bsZm+w39JXgFvytN2fqyl3bdog6p9QlX4CTn9plk2u0','172.25.0.1','curl/8.14.1','2026-10-02 02:11:04',0,'2026-09-25 02:11:04'),
(34,48,'$argon2id$v=19$m=65536,t=3,p=4$v7cWwrg3Rqh1bs0ZIwQAQA$15UhXcE9aGDRls6eDbU6JArQ6ufkwqPJAXl2n1VRe2E','172.25.0.1','curl/8.14.1','2026-10-02 02:11:04',0,'2026-09-25 02:11:04'),
(35,51,'$argon2id$v=19$m=65536,t=3,p=4$hhDCOIdwrjXmXGvNWUtJqQ$tD8BbxlVWlnonZEEgkGM5Y6lKvhZKdxC1G0Qd/Y+8A0','172.25.0.1','curl/8.14.1','2026-10-02 02:11:15',0,'2026-09-25 02:11:15'),
(36,48,'$argon2id$v=19$m=65536,t=3,p=4$hxACwBjDeI8xpjSGkPL+3w$yXk9Wcw6b8jkwwhj4SlExYV6nZFVcie15Bq4UEoC5PI','172.25.0.1','curl/8.14.1','2026-10-02 02:11:15',0,'2026-09-25 02:11:15'),
(37,51,'$argon2id$v=19$m=65536,t=3,p=4$kzLGWAuBcK6VknIuhRCi9A$psvi39BXhvtuF+wWX4MMOmHXmqF1PnsMqptrjVVbSEE','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/153.0.0.0 Safari/537.36','2026-10-02 02:11:27',0,'2026-09-25 02:11:27'),
(38,48,'$argon2id$v=19$m=65536,t=3,p=4$2vs/B0CIsXZOCUHoXWsNQQ$wf+5/EtGPUDzydui4YQeRsif/igSk0C5NbGKie+Ueco','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/153.0.0.0 Safari/537.36','2026-10-02 02:11:44',0,'2026-09-25 02:11:44'),
(39,50,'$argon2id$v=19$m=65536,t=3,p=4$tPa+9z4nxHgPwViLEQKg1A$oY8vCnB/ORwv4qawigVX6AkKXi+pv/iWzVc9S8aPFD0','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36','2026-10-02 02:12:29',0,'2026-09-25 02:12:29'),
(40,48,'$argon2id$v=19$m=65536,t=3,p=4$B4AwJiSklBKCUMo5JyRESA$5iQpLQqg6WvfMVEcQunxv7YYojQQ4zY5l5qMLXxALxc','172.25.0.1','curl/8.14.1','2026-10-02 02:20:41',0,'2026-09-25 02:20:41'),
(41,51,'$argon2id$v=19$m=65536,t=3,p=4$8D6ndK5VqjVm7H3P+Z/zPg$7AIvgC3/NII42LAo5LG/vPs7xT7ZU7Vlw7TduM3FpZY','172.25.0.1','curl/8.14.1','2026-10-02 02:20:41',0,'2026-09-25 02:20:41'),
(42,48,'$argon2id$v=19$m=65536,t=3,p=4$XSullDImZIwRAqDUWst5Lw$U7cp9w71hQiTvHnZTvdE4OoJ4wEL8E9QUAcvc5JxT5E','172.25.0.1','curl/8.14.1','2026-10-02 02:21:02',0,'2026-09-25 02:21:02'),
(44,48,'$argon2id$v=19$m=65536,t=3,p=4$b23tXYtRqnVuLWXsPQeA0A$/FiUG0JFIu++X3yWisR+FhFEWsXUYjqBhcXkHWheFwo','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/153.0.0.0 Safari/537.36','2026-10-02 02:21:16',0,'2026-09-25 02:21:16'),
(45,51,'$argon2id$v=19$m=65536,t=3,p=4$2tu7VwpB6D2H8J5zztk7Rw$Xb/ph9H8lv8rwUX5oID7XHdeUrirwzcU7tuRgw/vMOI','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/153.0.0.0 Safari/537.36','2026-10-02 02:21:20',0,'2026-09-25 02:21:20'),
(46,48,'$argon2id$v=19$m=65536,t=3,p=4$tNZ6zxljrJWylrKWcs4ZIw$i6QM8EHJO1keoVcpkygQUpp/vQnz4n0Nw/OCXCyWFlg','172.25.0.1','curl/8.14.1','2026-10-02 02:21:33',0,'2026-09-25 02:21:33'),
(47,48,'$argon2id$v=19$m=65536,t=3,p=4$1PrfW4sxhjAGoHQOoRSidA$G82NXigemG+VBsJwgN4YvBhcDd8eUOkJ9EvLE8C2DLk','172.25.0.1','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/153.0.0.0 Safari/537.36','2026-10-02 02:21:36',0,'2026-09-25 02:21:36'),
(48,48,'$argon2id$v=19$m=65536,t=3,p=4$Qci5d45xTklJ6d0753zvnQ$P6sg9IwxNsuXPTOxAqnnn4UtcC3JKNXl1sh/K0jV8cM','172.25.0.1','curl/8.14.1','2026-10-02 02:22:02',0,'2026-09-25 02:22:02');
/*!40000 ALTER TABLE `sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `totp_secrets`
--

DROP TABLE IF EXISTS `totp_secrets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `totp_secrets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `secret` varchar(255) NOT NULL,
  `backup_codes` text DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `totp_secrets_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `totp_secrets`
--

LOCK TABLES `totp_secrets` WRITE;
/*!40000 ALTER TABLE `totp_secrets` DISABLE KEYS */;
/*!40000 ALTER TABLE `totp_secrets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_roles`
--

DROP TABLE IF EXISTS `user_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_role` (`user_id`,`role_id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_roles`
--

LOCK TABLES `user_roles` WRITE;
/*!40000 ALTER TABLE `user_roles` DISABLE KEYS */;
INSERT INTO `user_roles` VALUES
(1,48,1),
(2,49,2),
(3,50,2),
(4,51,2),
(6,52,3),
(9,53,1),
(10,53,2),
(12,54,2),
(13,54,3);
/*!40000 ALTER TABLE `user_roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `full_name` varchar(150) DEFAULT NULL,
  `phone` varchar(30) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE','SUSPENDED') NOT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `totp_enabled` tinyint(1) NOT NULL,
  `failed_login_attempts` int(11) NOT NULL,
  `locked_until` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_city` (`city`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES
(40,'productor1@test.com','password123','Productor 1','0000001','Córdoba','ACTIVE',1,0,0,NULL,'2026-09-24 22:50:43','2026-09-24 22:50:43',NULL),
(41,'productor2@test.com','password123','Productor 2','0000002','Mendoza','ACTIVE',1,0,0,NULL,'2026-09-24 22:50:43','2026-09-24 22:50:43',NULL),
(42,'productor3@test.com','password123','Productor 3','0000003','Mendoza','ACTIVE',1,0,0,NULL,'2026-09-24 22:50:43','2026-09-24 22:50:43',NULL),
(43,'productor4@test.com','password123','Productor 4','0000004','Mendoza','ACTIVE',1,0,0,NULL,'2026-09-24 22:50:43','2026-09-24 22:50:43',NULL),
(44,'productor5@test.com','password123','Productor 5','0000005','Buenos Aires','ACTIVE',1,0,0,NULL,'2026-09-24 22:50:43','2026-09-24 22:50:43',NULL),
(45,'productor6@test.com','password123','Productor 6','0000006','Buenos Aires','ACTIVE',1,0,0,NULL,'2026-09-24 22:50:43','2026-09-24 22:50:43',NULL),
(46,'productor7@test.com','password123','Productor 7','0000007','Córdoba','ACTIVE',1,0,0,NULL,'2026-09-24 22:50:43','2026-09-24 22:50:43',NULL),
(47,'productor8@test.com','password123','Productor 8','0000008','Córdoba','ACTIVE',1,0,0,NULL,'2026-09-24 22:50:43','2026-09-24 22:50:43',NULL),
(48,'admin@plpe.com','$argon2id$v=19$m=65536,t=3,p=4$QiglZGwNYczZm9N6T6lVyg$dfc2O025slO7yzKVJGfKA2Aj1YRHpkNlK/4Pc7SWVWw','Administrador PLPE',NULL,NULL,'ACTIVE',1,0,0,NULL,'2026-09-24 23:03:04','2026-09-25 02:04:28',NULL),
(49,'jorge@jorge.com','$argon2id$v=19$m=65536,t=3,p=4$X6vVWstZa43xnnNuDaH0fg$7DgSEwPSK9dOTQoZPCM4rzGZFzeb59v937FkqevY3jM','jorge rojas','3704367698','formosa','ACTIVE',0,0,0,NULL,'2026-09-25 02:02:02','2026-09-25 02:02:02',NULL),
(50,'jorge@luis.com','$argon2id$v=19$m=65536,t=3,p=4$qbVWipGyNgbAOKd0LsWYMw$4Pe0zdpjsMpxT1v3+KpWlqvHOdsxtdcFbW7rR6Qn1rs','jorge rojas','+543705237246','formosa','ACTIVE',0,0,0,NULL,'2026-09-25 02:06:46','2026-09-25 02:06:46',NULL),
(51,'prod_test@plpe.com','$argon2id$v=19$m=65536,t=3,p=4$l7L2/l9L6T0H4FzrHcP4fw$jk4tYULWG94g3ZB6LKaZMUL0lq6DO/OoE68sdtEDsr0','Productor Test',NULL,'Formosa','ACTIVE',0,0,0,NULL,'2026-09-25 02:11:04','2026-09-25 02:11:04',NULL),
(52,'borrar@plpe.com','$argon2id$v=19$m=65536,t=3,p=4$rvW+N4YQYmyttZaydg4BgA$0iXP4zR5NiuYpqS+ayCIC6alxDCEqnVanexlD5pPMf4','Para Borrar',NULL,NULL,'INACTIVE',0,0,0,NULL,'2026-09-25 02:20:42','2026-09-25 02:20:42','2026-09-25 02:20:42'),
(53,'roles_test@plpe.com','$argon2id$v=19$m=65536,t=3,p=4$/f+fMwagtLbWujemtDYm5A$yrYdWtCGrD5KaiB/985dCpsFLbHcJKBBGCTlMEybNzk','Roles Test',NULL,NULL,'INACTIVE',0,0,0,NULL,'2026-09-25 02:21:02','2026-09-25 02:21:03','2026-09-25 02:21:03'),
(54,'ui_del@plpe.com','$argon2id$v=19$m=65536,t=3,p=4$KKXUOocw5lzrnRPivDcGgA$K7gFHQptkQbZgGKtW7BA9WsSMDXPltwpW4i7DJUA0wE','UI Delete',NULL,NULL,'INACTIVE',0,0,0,NULL,'2026-09-25 02:21:33','2026-09-25 02:21:42','2026-09-25 02:21:42');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-25  2:30:02
