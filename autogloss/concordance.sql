-- MySQL dump 10.13  Distrib 5.7.24, for Linux (x86_64)
--
-- Host: localhost    Database: rutul_concord
-- ------------------------------------------------------
-- Server version	5.7.24-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `basic_info`
--

DROP TABLE IF EXISTS `basic_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `basic_info` (
  `inx` int(11) NOT NULL AUTO_INCREMENT,
  `correct_morph` longtext,
  `POS` longtext,
  `lemma` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`inx`),
  UNIQUE KEY `inx_UNIQUE` (`inx`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `basic_info`
--

LOCK TABLES `basic_info` WRITE;
/*!40000 ALTER TABLE `basic_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `basic_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `correction`
--

DROP TABLE IF EXISTS `correction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `correction` (
  `id_correct_morph` int(11) DEFAULT NULL,
  `written_variants` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `correction`
--

LOCK TABLES `correction` WRITE;
/*!40000 ALTER TABLE `correction` DISABLE KEYS */;
/*!40000 ALTER TABLE `correction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `glosses`
--

DROP TABLE IF EXISTS `glosses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `glosses` (
  `id_correct_morph` int(11) DEFAULT NULL,
  `gloss_variants` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `glosses`
--

LOCK TABLES `glosses` WRITE;
/*!40000 ALTER TABLE `glosses` DISABLE KEYS */;
/*!40000 ALTER TABLE `glosses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stripped`
--

DROP TABLE IF EXISTS `stripped`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stripped` (
  `id_correct_morph` int(11) DEFAULT NULL,
  `stripped_correct_forms` varchar(45) DEFAULT NULL,
  `stripped_written_variants` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stripped`
--

LOCK TABLES `stripped` WRITE;
/*!40000 ALTER TABLE `stripped` DISABLE KEYS */;
/*!40000 ALTER TABLE `stripped` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-12-11  0:41:47
