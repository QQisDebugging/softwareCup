-- MySQL dump 10.13  Distrib 8.0.37, for Win64 (x86_64)
--
-- Host: 114.55.147.180    Database: pwxiao
-- ------------------------------------------------------
-- Server version	5.7.33-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activity`
--

DROP TABLE IF EXISTS `activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity` (
  `activity_id` int(11) NOT NULL AUTO_INCREMENT,
  `activity_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `creator_tno` int(11) NOT NULL,
  `description` mediumtext COLLATE utf8mb4_unicode_ci,
  `created_date` date NOT NULL,
  PRIMARY KEY (`activity_id`),
  KEY `creator_tno` (`creator_tno`),
  CONSTRAINT `activity_ibfk_1` FOREIGN KEY (`creator_tno`) REFERENCES `teacher` (`tno`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity`
--

LOCK TABLES `activity` WRITE;
/*!40000 ALTER TABLE `activity` DISABLE KEYS */;
INSERT INTO `activity` (`activity_id`, `activity_name`, `creator_tno`, `description`, `created_date`) VALUES (1,'acm校赛',2000001,'为了激发大家计算机热情','2024-05-08'),(3,'六一儿童节',2000001,'为了庆祝六一儿童节','2024-06-03'),(5,'如何养猪',2000001,'如何养猪','2024-06-01'),(12,'计算机组成原理实验',2000001,'提交文档','2024-06-03'),(15,'大模型技术讨论',2000002,'请同学们在评论区发言讨论大模型技术的优势与劣势','2024-06-04'),(16,'志愿',2000003,'','2024-06-15'),(17,'计算机组成原理',8888888,'','2024-06-18');
/*!40000 ALTER TABLE `activity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `activity_classes`
--

DROP TABLE IF EXISTS `activity_classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity_classes` (
  `activity_id` int(11) NOT NULL,
  `class_id` int(11) NOT NULL,
  PRIMARY KEY (`activity_id`,`class_id`),
  KEY `activity_classes_ibfk_2` (`class_id`),
  CONSTRAINT `activity_classes_ibfk_1` FOREIGN KEY (`activity_id`) REFERENCES `activity` (`activity_id`),
  CONSTRAINT `activity_classes_ibfk_2` FOREIGN KEY (`class_id`) REFERENCES `classes` (`ClassID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity_classes`
--

LOCK TABLES `activity_classes` WRITE;
/*!40000 ALTER TABLE `activity_classes` DISABLE KEYS */;
INSERT INTO `activity_classes` (`activity_id`, `class_id`) VALUES (5,1),(16,1),(17,1),(5,2),(5,3);
/*!40000 ALTER TABLE `activity_classes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classes`
--

DROP TABLE IF EXISTS `classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classes` (
  `ClassID` int(11) NOT NULL AUTO_INCREMENT,
  `ClassName` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `MajorID` int(11) DEFAULT NULL,
  `GradeID` int(11) DEFAULT NULL,
  PRIMARY KEY (`ClassID`),
  KEY `GradeID` (`GradeID`),
  KEY `MajorID` (`MajorID`),
  CONSTRAINT `classes_ibfk_1` FOREIGN KEY (`MajorID`) REFERENCES `majors` (`MajorID`),
  CONSTRAINT `classes_ibfk_2` FOREIGN KEY (`GradeID`) REFERENCES `grades` (`GradeID`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classes`
--

LOCK TABLES `classes` WRITE;
/*!40000 ALTER TABLE `classes` DISABLE KEYS */;
INSERT INTO `classes` (`ClassID`, `ClassName`, `MajorID`, `GradeID`) VALUES (1,'计算机22-1',1,2),(2,'计算机22-2',1,2),(3,'计算机22-3',1,2),(4,'计算机22-4',1,2),(5,'计算机22-5',1,2),(6,'计算机22-6',1,2),(7,'计算机22-7',1,2),(8,'计算机22-8',1,2),(9,'计算机22-9',1,2),(10,'计算机22-10',1,2),(11,'软件工程22-1',2,2),(12,'软件工程22-2',2,2),(13,'数字媒体22-1',3,2),(14,'数字媒体22-2',3,2),(17,'信息安全22-1',4,2),(18,'信息安全22-2',4,2),(19,'物联网22-1',5,2),(20,'物联网22-2',5,2),(21,'区块链22-1',6,2);
/*!40000 ALTER TABLE `classes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contest`
--

DROP TABLE IF EXISTS `contest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contest` (
  `contest_id` int(11) NOT NULL AUTO_INCREMENT,
  `contest_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `creator_tno` int(11) NOT NULL,
  `question_json` json NOT NULL,
  `question_type` enum('选择题','判断题','问答题') COLLATE utf8mb4_unicode_ci NOT NULL,
  `publish_date` datetime NOT NULL,
  PRIMARY KEY (`contest_id`),
  KEY `idx_creator_tno` (`creator_tno`),
  CONSTRAINT `contest_ibfk_1` FOREIGN KEY (`creator_tno`) REFERENCES `teacher` (`tno`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contest`
--

LOCK TABLES `contest` WRITE;
/*!40000 ALTER TABLE `contest` DISABLE KEYS */;
INSERT INTO `contest` (`contest_id`, `contest_name`, `creator_tno`, `question_json`, `question_type`, `publish_date`) VALUES (3,'数据库操作',2000001,'[{\"答案\": 1, \"选项\": [\"数据存储在表中\", \"数据之间无关联\", \"使用SQL进行数据管理\", \"提供数据完整性保障\"], \"题目\": \"以下哪个不是关系型数据库的基本特性？\"}, {\"答案\": 0, \"选项\": [\"SELECT *\", \"INSERT INTO\", \"UPDATE\", \"DELETE\"], \"题目\": \"在SQL中，用于从表中选取所有列和行的语句是？\"}, {\"答案\": 2, \"选项\": [\"删除数据\", \"更新数据\", \"连接两个或多个表中的数据\", \"创建新表\"], \"题目\": \"SQL中的JOIN操作主要用于什么？\"}, {\"答案\": 3, \"选项\": [\"Create\", \"Read\", \"Update\", \"Search\"], \"题目\": \"在数据库中，以下哪个操作不是CRUD操作的一部分？\"}, {\"答案\": 2, \"选项\": [\"主键约束\", \"外键约束\", \"唯一约束\", \"检查约束\"], \"题目\": \"以下哪种约束用于确保表中某列的数据唯一？\"}, {\"答案\": 0, \"选项\": [\"INSERT INTO\", \"SELECT\", \"DELETE\", \"UPDATE\"], \"题目\": \"SQL中，用于插入新数据到表中的语句是？\"}, {\"答案\": 2, \"选项\": [\"索引\", \"表\", \"键\", \"视图\"], \"题目\": \"在关系型数据库中，用于描述实体之间联系的是？\"}, {\"答案\": 1, \"选项\": [\"数据安全性\", \"数据完整性\", \"数据并发性\", \"数据冗余性\"], \"题目\": \"SQL中的事务主要用于确保什么？\"}, {\"答案\": 4, \"选项\": [\"需求分析\", \"概念设计\", \"逻辑设计\", \"物理设计\", \"随机设计\"], \"题目\": \"以下哪个不是数据库设计的主要阶段？\"}, {\"答案\": 0, \"选项\": [\"DELETE\", \"DROP\", \"TRUNCATE\", \"REMOVE\"], \"题目\": \"在SQL中，用于从表中删除数据的语句是？\"}]','选择题','2024-06-05 07:44:20'),(4,'数据库原理选择题',2000001,'[{\"答案\": 3, \"选项\": [\"定义数据的存储结构\", \"提供数据的安全性和完整性\", \"进行数据的物理存储\", \"负责数据的网络传输\"], \"题目\": \"以下哪个选项不是数据库管理系统(DBMS)的主要功能？\"}, {\"答案\": 3, \"选项\": [\"选择\", \"投影\", \"并\", \"插入\"], \"题目\": \"在关系数据库中，以下哪个不是关系运算？\"}, {\"答案\": 0, \"选项\": [\"加快查询速度\", \"保证数据的完整性\", \"存储数据的物理位置\", \"防止数据的丢失\"], \"题目\": \"SQL中的索引主要用于什么目的？\"}, {\"答案\": 0, \"选项\": [\"数据的逻辑结构\", \"数据的物理存储\", \"数据的通信协议\", \"数据的并发控制\"], \"题目\": \"在数据库设计中，E-R图主要用于描述什么？\"}]','选择题','2024-06-05 08:25:19'),(5,'程序设计基础判断题',2000001,'[{\"答案\": \"0\", \"题目\": \"在程序设计中，变量名通常用于标识程序中使用的各种数据。\"}, {\"答案\": \"1\", \"题目\": \"所有的编程语言都支持面向对象的程序设计方式。\"}, {\"答案\": \"0\", \"题目\": \"在程序设计中，注释是用于解释代码功能或作用的文字，对程序执行没有影响。\"}]','判断题','2024-06-05 08:37:07'),(6,'python基础简答题',2000002,'[{\"答案\": \"在Python中，使用`def`关键字定义函数。例如：`def greet(name): return \'Hello, \' + name`。这个函数接受一个参数`name`，并返回问候语。\", \"题目\": \"Python中，如何定义一个函数？请给出一个简单的例子。\"}, {\"答案\": \"列表（list）是可变的，可以添加、删除或修改元素；而元组（tuple）是不可变的，一旦创建就不能修改其内容。列表使用方括号`[]`，元组使用圆括号`()`。\", \"题目\": \"解释Python中的列表（list）和元组（tuple）的主要区别。\"}, {\"答案\": \"在Python中，使用键（key）来访问字典中的元素。例如，`my_dict = {\'name\': \'Alice\', \'age\': 30}`，则可以通过`my_dict[\'name\']`获取\'Alice\'。\", \"题目\": \"在Python中，如何访问字典（dictionary）中的元素？请给出示例。\"}, {\"答案\": \"Python中的异常处理机制通过try-except结构实现。try块中放可能引发异常的代码，except块捕获并处理异常。这有助于程序在出错时仍能优雅地运行，而不是直接崩溃。\", \"题目\": \"描述Python中的异常处理机制，包括try-except结构的作用。\"}]','问答题','2024-06-05 09:17:23'),(7,'如何养猪',2000001,'[{\"答案\": \"养猪的基本步骤包括：选择优良品种、建立合适的猪舍、准备充足的饲料和水源、做好卫生防疫工作、合理饲养管理、定期检查和记录猪只的生长情况。\", \"题目\": \"简述养猪的基本步骤。\"}, {\"答案\": \"常见的猪饲料有玉米、豆粕、麦麸、鱼粉、骨粉等。这些饲料富含蛋白质、矿物质和维生素，有助于猪只的生长和发育。\", \"题目\": \"请列举几种常见的猪饲料。\"}, {\"答案\": \"要保证猪舍的卫生环境，需要定期清理猪舍内的粪便和杂物，保持猪舍干燥通风，并定期对猪舍进行消毒处理。\", \"题目\": \"在养猪过程中，如何保证猪舍的卫生环境？\"}, {\"答案\": \"猪只的疫苗接种程序通常包括猪瘟、猪肺疫、猪丹毒等多种疫苗，接种时间、剂量和间隔需根据疫苗种类和猪只生长阶段来确定。\", \"题目\": \"简述猪只的疫苗接种程序。\"}, {\"答案\": \"要合理控制饲料成本，可以选择价格合理、质量可靠的饲料供应商，避免浪费和过度饲喂，同时根据猪只的生长阶段和营养需求调整饲料配方。\", \"题目\": \"在养猪过程中，如何合理控制饲料成本？\"}]','问答题','2024-06-05 10:26:00'),(8,'五代机优劣对比',2000001,'[{\"答案\": 2, \"选项\": [\"五代机具有隐身能力\", \"五代机通常配备先进的雷达系统\", \"五代机无法执行超音速巡航\", \"五代机拥有高机动性\"], \"题目\": \"下列关于五代机的描述，错误的是？\"}, {\"答案\": 4, \"选项\": [\"隐身性能\", \"超音速巡航能力\", \"作战半径\", \"最大飞行速度\"], \"题目\": \"五代机相对于四代机，以下哪项不是显著的提升？\"}, {\"答案\": 2, \"选项\": [\"外形设计优化\", \"吸波材料使用\", \"增大雷达反射面积\", \"降低红外辐射\"], \"题目\": \"五代机通常采用的隐身技术不包括？\"}, {\"答案\": 1, \"选项\": [\"五代机都不具备超音速巡航能力\", \"超音速巡航能力是五代机的基本特征之一\", \"五代机的超音速巡航速度与普通飞机无异\", \"五代机只能在短时间内进行超音速巡航\"], \"题目\": \"下列关于五代机超音速巡航能力的说法，正确的是？\"}, {\"答案\": 2, \"选项\": [\"强大的雷达探测能力\", \"优秀的网络战能力\", \"高速的数据处理能力\", \"较长的滞空时间\"], \"题目\": \"五代机在信息战方面的优势主要体现在？\"}, {\"答案\": 3, \"选项\": [\"美国\", \"俄罗斯\", \"中国\", \"印度\"], \"题目\": \"以下哪个国家目前尚未推出自己的五代机？\"}]','选择题','2024-06-05 10:36:13'),(9,'如何缓解颈椎',2000001,'[{\"答案\": \"0\", \"题目\": \"长时间保持同一姿势是导致腰痛和颈椎疼的主要原因之一。\"}, {\"答案\": \"0\", \"题目\": \"适当的运动可以有效缓解腰痛和颈椎疼。\"}, {\"答案\": \"1\", \"题目\": \"腰痛和颈椎疼只能通过药物治疗。\"}, {\"答案\": \"1\", \"题目\": \"正确的坐姿和站姿对预防腰痛和颈椎疼没有帮助。\"}]','判断题','2024-06-05 10:42:54'),(10,'计算机组成原理习题',2000001,'[{\"答案\": 1, \"选项\": [\"逻辑运算\", \"算术运算\", \"存储操作\", \"输入输出操作\"], \"题目\": \"计算机中的ALU主要执行哪种操作？\"}, {\"答案\": 2, \"选项\": [\"提高CPU速度\", \"提高主存速度\", \"减少CPU与主存之间的速度差异\", \"增大存储空间\"], \"题目\": \"在计算机中，Cache的主要作用是？\"}, {\"答案\": 3, \"选项\": [\"指令集是CPU能理解和执行的指令的集合\", \"不同的CPU架构可能采用不同的指令集\", \"指令集是软件与硬件之间的接口\", \"指令集越复杂，CPU性能一定越高\"], \"题目\": \"下列关于指令集的说法中，不正确的是？\"}, {\"答案\": 3, \"选项\": [\"提高存储速度\", \"扩大存储容量\", \"降低存储成本\", \"增加存储功耗\"], \"题目\": \"在计算机的存储器层次结构中，以下哪项不是其设计的主要目标？\"}, {\"答案\": 3, \"选项\": [\"实现多道程序并发执行\", \"实现CPU与I/O设备之间的并行工作\", \"处理异常情况或错误\", \"提高CPU的运算速度\"], \"题目\": \"中断是计算机中的一个重要概念，其主要作用不包括？\"}, {\"答案\": 2, \"选项\": [\"连接CPU与主存\", \"连接CPU与I/O设备\", \"连接计算机内部各个部件\", \"连接计算机与外部设备\"], \"题目\": \"在计算机中，总线的主要作用是什么？\"}, {\"答案\": 2, \"选项\": [\"存储器的访问速度\", \"CPU的运算速度\", \"指令的执行速度\", \"数据传输的带宽\"], \"题目\": \"计算机中的流水线技术主要用于提高哪种性能？\"}, {\"答案\": 0, \"选项\": [\"扩大主存容量\", \"提高CPU运算速度\", \"增强I/O设备性能\", \"简化程序设计\"], \"题目\": \"在计算机中，虚拟存储器的概念主要解决什么问题？\"}, {\"答案\": 1, \"选项\": [\"DMA方式中，数据的传送完全由CPU控制\", \"DMA方式中，数据的传送不经过CPU\", \"DMA方式不能用于磁盘与主存之间的数据传送\", \"DMA方式比中断方式传送数据更慢\"], \"题目\": \"关于DMA方式，以下说法正确的是？\"}, {\"答案\": 3, \"选项\": [\"更大的存储空间\", \"更快的执行速度\", \"更高级的错误检测\", \"更强的内存保护\"], \"题目\": \"在计算机中，保护模式相比于实模式，提供了什么功能？\"}]','选择题','2024-06-05 11:42:33'),(11,'模拟数字电路',2000005,'[{\"答案\": \"0\", \"题目\": \"模拟数字电路是处理连续变化的物理量的电路。\"}, {\"答案\": \"1\", \"题目\": \"模拟数字电路中的信号只能是数字信号。\"}, {\"答案\": \"0\", \"题目\": \"在模拟数字电路中，可以使用模拟开关来控制电路的通断。\"}, {\"答案\": \"1\", \"题目\": \"模拟数字电路中的运算放大器只能用于放大模拟信号。\"}, {\"答案\": \"0\", \"题目\": \"数模转换器是将数字信号转换为模拟信号的电路元件。\"}, {\"答案\": \"1\", \"题目\": \"模数转换器在模拟数字电路中没有实际应用价值。\"}, {\"答案\": \"0\", \"题目\": \"在模拟数字电路中，滤波器通常用于消除不需要的频率成分。\"}, {\"答案\": \"1\", \"题目\": \"模拟数字电路中的比较器只能比较两个模拟信号的大小。\"}, {\"答案\": \"0\", \"题目\": \"采样定理是模拟数字电路中的一个重要原理，它描述了模拟信号转换为数字信号时的最低采样频率要求。\"}, {\"答案\": \"0\", \"题目\": \"在模拟数字电路中，量化误差是不可避免的。\"}, {\"答案\": \"1\", \"题目\": \"模拟数字电路中的D/A转换器可以将数字信号直接转换为模拟信号，无需任何处理。\"}, {\"答案\": \"0\", \"题目\": \"A/D转换器在模拟数字电路中起着将模拟信号转换为数字信号的关键作用。\"}, {\"答案\": \"1\", \"题目\": \"在模拟数字电路中，信号的放大只能通过运算放大器实现。\"}, {\"答案\": \"0\", \"题目\": \"模拟数字电路中的反馈电路通常用于改善电路的性能和稳定性。\"}, {\"答案\": \"0\", \"题目\": \"模拟数字电路中的振荡器可以产生稳定的正弦波信号。\"}, {\"答案\": \"1\", \"题目\": \"在模拟数字电路中，数字信号的处理速度通常比模拟信号慢。\"}, {\"答案\": \"0\", \"题目\": \"模拟数字电路中的逻辑门电路只能处理数字信号，不能处理模拟信号。\"}, {\"答案\": \"1\", \"题目\": \"模拟数字电路中的所有元件都是线性的。\"}, {\"答案\": \"0\", \"题目\": \"在模拟数字电路中，非线性元件可以用于实现各种复杂的信号处理功能。\"}]','判断题','2024-06-05 12:43:51'),(12,'计算机组成原理',2000003,'[{\"答案\": \"0\", \"题目\": \"在计算机组成原理中，指令集是处理器硬件能够直接识别和执行的一组指令的集合。\"}, {\"答案\": \"0\", \"题目\": \"CPU的主频越高，表示CPU的速度越快。\"}, {\"答案\": \"0\", \"题目\": \"在计算机组成中，主存储器通常使用RAM（随机存取存储器）作为其主要存储介质。\"}, {\"答案\": \"0\", \"题目\": \"总线是用于连接计算机各个部件的一组共享导线，可以传输数据、地址和控制信息。\"}, {\"答案\": \"0\", \"题目\": \"中断是CPU对系统发生的某个事件作出的一种反应，它可以使CPU暂停当前正在执行的程序，转去执行另一段处理该事件的程序。\"}, {\"答案\": \"0\", \"题目\": \"在计算机组成原理中，高速缓存（Cache）的主要目的是增加CPU访问主存的速度。\"}]','判断题','2024-06-10 05:31:53'),(13,'围棋入门',2000001,'[{\"答案\": 2, \"选项\": [\"双方互相提对方的子\", \"在对方的棋形中制造断点\", \"双方轮流提走对方一子，直至一方无法继续\", \"在一方棋子旁边紧挨着下子\"], \"题目\": \"围棋中，什么是“打劫”？\"}, {\"答案\": 3, \"选项\": [\"在对方的两颗子之间下子\", \"两颗己方棋子并排且间隔一路\", \"两颗己方棋子并排且间隔两路\", \"在对方棋子两侧同时下子，形成钳制\"], \"题目\": \"围棋中的“双飞燕”通常指的是什么棋形？\"}, {\"答案\": 2, \"选项\": [\"先下两子形成小尖，再拆边至三路线\", \"在角部形成两个相邻的棋子，然后拆到边部\", \"在角部形成两个间隔一路的棋子，然后拆到三路线\", \"在边部连续下三子，形成一条直线\"], \"题目\": \"在围棋中，什么是“立二拆三”的开局策略？\"}]','选择题','2024-06-11 16:51:06'),(14,'足球',2000003,'[{\"答案\": \"0\", \"题目\": \"足球比赛中，每个队伍都有11名球员在场上比赛。\"}, {\"答案\": \"0\", \"题目\": \"在足球比赛中，越位是指球员在传球时，接球的队友站在比最后一名防守球员和门将更靠近球门线的位置。\"}, {\"答案\": \"1\", \"题目\": \"足球比赛中的红牌表示警告，黄牌表示罚出场。\"}]','判断题','2024-06-15 18:06:43'),(15,'计算机基础知识',2000001,'[{\"答案\": 1, \"选项\": [\"CPU\", \"内存\", \"硬盘\", \"显卡\"], \"题目\": \"在计算机中，用于临时存储数据和指令的部件是？\"}, {\"答案\": 2, \"选项\": [\"CPU\", \"内存\", \"硬盘\", \"显示器\"], \"题目\": \"计算机中，用于长期存储数据和程序的设备通常是？\"}, {\"答案\": 0, \"选项\": [\"CPU\", \"内存\", \"硬盘\", \"声卡\"], \"题目\": \"在计算机中，负责执行指令和进行算术逻辑运算的部件是？\"}, {\"答案\": 3, \"选项\": [\"CPU\", \"内存\", \"硬盘\", \"显示器\"], \"题目\": \"以下哪个部件不是计算机主机的一部分？\"}, {\"答案\": 2, \"选项\": [\"键盘\", \"鼠标\", \"显示器\", \"打印机\"], \"题目\": \"计算机中，用于显示图像和视频信息的设备是？\"}, {\"答案\": 2, \"选项\": [\"显示器\", \"打印机\", \"键盘\", \"音箱\"], \"题目\": \"以下哪个设备是计算机的输入设备？\"}, {\"答案\": 3, \"选项\": [\"管理计算机硬件\", \"管理计算机软件\", \"提供用户界面\", \"代替CPU执行指令\"], \"题目\": \"在计算机中，操作系统的主要功能不包括？\"}, {\"答案\": 3, \"选项\": [\"系统软件\", \"应用软件\", \"中间件\", \"电子硬件\"], \"题目\": \"以下哪个不是计算机软件的分类？\"}, {\"答案\": 3, \"选项\": [\"8\", \"9\", \"10\", \"11\"], \"题目\": \"二进制数1011转换为十进制数是多少？\"}, {\"答案\": 2, \"选项\": [\"4\", \"6\", \"8\", \"10\"], \"题目\": \"一个字节由多少个二进制位组成？\"}, {\"答案\": 1, \"选项\": [\"位\", \"字节\", \"字\", \"KB\"], \"题目\": \"计算机中，数据的基本单位是？\"}]','选择题','2024-06-18 09:57:17'),(16,'计算机网络',2000001,'[{\"答案\": \"计算机网络由多个独立的计算机和通信设备组成，通过传输介质相互连接。其功能包括资源共享、数据传输、负载均衡和分布式处理等。\", \"题目\": \"请简述计算机网络的基本组成和功能。\"}, {\"答案\": \"OSI七层模型包括物理层、数据链路层、网络层、传输层、会话层、表示层和应用层。各层分别负责物理连接、数据帧封装、路由选择、端到端传输、会话管理、数据表示和应用程序接口等功能。\", \"题目\": \"解释什么是OSI七层模型，并简述每一层的主要功能。\"}, {\"答案\": \"TCP是面向连接的、可靠的、基于字节流的传输层协议；UDP是无连接的、不可靠的、基于数据报的传输层协议。TCP提供数据重传、流量控制和拥塞控制等机制，适用于需要可靠传输的应用；UDP简单高效，适用于实时性要求较高、允许丢包的应用。\", \"题目\": \"请解释TCP和UDP之间的主要区别。\"}, {\"答案\": \"IP地址是逻辑地址，用于在网络层标识设备；MAC地址是物理地址，用于数据链路层标识设备。IP地址可以改变，而MAC地址通常固定不变。IP地址用于跨网络的通信，而MAC地址用于同一局域网内的通信。\", \"题目\": \"简述IP地址和MAC地址的区别。\"}, {\"答案\": \"ARP协议是地址解析协议，用于将网络层的IP地址解析为数据链路层的MAC地址。它在同一局域网内广播ARP请求，以获取目标设备的MAC地址，从而建立通信。\", \"题目\": \"请解释什么是ARP协议，它的作用是什么？\"}, {\"答案\": \"路由器是网络层设备，负责在网络间转发数据包。它根据路由表选择最佳路径，实现不同网络之间的互联互通，同时提供网络隔离和安全控制功能。\", \"题目\": \"请简述路由器在计算机网络中的作用。\"}, {\"答案\": \"网络协议是计算机网络中通信双方必须共同遵守的规则和约定。它定义了数据格式、通信方式、错误检测与处理等，以确保数据的正确传输和解析。没有网络协议，计算机之间的通信将无法进行。\", \"题目\": \"什么是网络协议？为什么需要网络协议？\"}, {\"答案\": \"DNS域名解析过程包括客户端发送域名查询请求给本地DNS服务器，本地DNS服务器递归或迭代查询根域名服务器、顶级域名服务器和权威域名服务器，最终获取IP地址并返回给客户端。\", \"题目\": \"请简述DNS域名解析的过程。\"}, {\"答案\": \"网络拓扑结构是指网络中各节点与通信线路之间的几何关系。常见的网络拓扑结构包括星型、环型、总线型、树型和网状型等。\", \"题目\": \"解释什么是网络拓扑结构，并列举几种常见的网络拓扑结构。\"}, {\"答案\": \"CSMA/CD（载波监听多路访问/碰撞检测）协议是以太网中使用的介质访问控制方法。它要求发送数据前先监听信道是否空闲，若空闲则发送数据，并同时监听是否有碰撞发生，若有则停止发送并等待一段时间后重试。\", \"题目\": \"请简述CSMA/CD协议的工作原理。\"}, {\"答案\": \"VLAN是虚拟局域网，它将一个物理局域网划分为多个逻辑子网。VLAN可以实现广播域的隔离，提高网络的安全性和灵活性，同时降低网络管理成本。\", \"题目\": \"什么是VLAN？它在网络中的作用是什么？\"}, {\"答案\": \"NAT用于将私有IP地址转换为公有IP地址，实现内部网络与外部网络的互联互通。它工作在IP层，通过修改数据包的源或目的IP地址和端口号，实现地址转换和端口复用。\", \"题目\": \"请简述NAT（网络地址转换）的作用和工作原理。\"}, {\"答案\": \"防火墙是网络安全设备，用于监控和控制进出网络的流量。其主要功能包括访问控制、内容过滤、安全审计和VPN支持等，以保护网络免受未经授权的访问和攻击。\", \"题目\": \"请解释什么是防火墙，并列举其主要功能。\"}, {\"答案\": \"无线局域网利用无线通信技术实现设备间的互联互通。其常见应用场景包括家庭网络、办公室网络、公共场所网络等，为用户提供便捷的网络接入服务。\", \"题目\": \"请简述什么是无线局域网，并列举其常见的应用场景。\"}]','问答题','2024-06-19 02:20:10'),(17,'数据库原理',8888888,'[{\"答案\": 1, \"选项\": [\"数据库的物理结构\", \"数据库的逻辑结构\", \"数据库的存储过程\", \"数据库的查询语句\"], \"题目\": \"在数据库设计中，E-R图（实体-关系图）主要用于描述什么？\"}, {\"答案\": 1, \"选项\": [\"提高查询效率\", \"标识记录的唯一性\", \"用于连接多个表\", \"存储数据的顺序\"], \"题目\": \"关系数据库中的主键（Primary Key）的主要作用是什么？\"}, {\"答案\": 2, \"选项\": [\"数据存储在表格中\", \"表格之间通过关系连接\", \"数据以文件形式存储\", \"支持SQL语言进行数据操作\"], \"题目\": \"以下哪项不是关系数据库管理系统的基本特点？\"}, {\"答案\": 0, \"选项\": [\"减少数据冗余\", \"提高查询速度\", \"增加存储空间\", \"简化数据库结构\"], \"题目\": \"在数据库设计中，规范化（Normalization）的主要目的是什么？\"}, {\"答案\": 1, \"选项\": [\"INSERT\", \"DELETE\", \"UPDATE\", \"SELECT\"], \"题目\": \"在SQL中，用于从表中删除记录的语句是？\"}, {\"答案\": 3, \"选项\": [\"创建新表\", \"删除表中的记录\", \"更新表中的记录\", \"根据条件合并两个或多个表的记录\"], \"题目\": \"在数据库查询中，JOIN操作的主要作用是什么？\"}, {\"答案\": 1, \"选项\": [\"提高查询效率\", \"保证数据的完整性\", \"实现数据的加密\", \"定义数据的存储格式\"], \"题目\": \"数据库中的外键（Foreign Key）主要用于什么目的？\"}, {\"答案\": 3, \"选项\": [\"实体完整性\", \"参照完整性\", \"字段完整性\", \"网络完整性\"], \"题目\": \"在关系型数据库中，以下哪个不是常见的数据完整性约束？\"}, {\"答案\": 2, \"选项\": [\"DELETE\", \"UPDATE\", \"SELECT\", \"CREATE\"], \"题目\": \"在SQL中，用于从表中检索数据的语句是？\"}, {\"答案\": 0, \"选项\": [\"简化复杂查询\", \"存储数据\", \"提高查询速度\", \"保护数据的完整性\"], \"题目\": \"数据库中的视图（View）主要用于什么目的？\"}, {\"答案\": 3, \"选项\": [\"提高查询速度\", \"降低插入速度\", \"加速表连接\", \"减少存储空间\"], \"题目\": \"以下哪个不是数据库索引（Index）的主要优点？\"}]','选择题','2024-06-24 15:14:24');
/*!40000 ALTER TABLE `contest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contest_class`
--

DROP TABLE IF EXISTS `contest_class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contest_class` (
  `contest_id` int(11) NOT NULL,
  `class_id` int(11) NOT NULL,
  PRIMARY KEY (`contest_id`,`class_id`),
  KEY `contest_class_ibfk_2` (`class_id`),
  CONSTRAINT `contest_class_ibfk_1` FOREIGN KEY (`contest_id`) REFERENCES `contest` (`contest_id`),
  CONSTRAINT `contest_class_ibfk_2` FOREIGN KEY (`class_id`) REFERENCES `classes` (`ClassID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contest_class`
--

LOCK TABLES `contest_class` WRITE;
/*!40000 ALTER TABLE `contest_class` DISABLE KEYS */;
INSERT INTO `contest_class` (`contest_id`, `class_id`) VALUES (3,1),(4,1),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1),(12,1),(13,1),(14,1),(15,1),(16,1),(6,2),(7,2),(8,2),(9,2),(10,2),(11,2),(12,2),(13,2),(14,2),(15,2),(17,2),(6,3),(7,3),(8,3),(9,3),(10,3),(11,3),(12,3),(13,3),(15,3),(17,3),(6,4),(7,4),(8,4),(9,4),(10,4),(11,4),(12,4),(13,4),(15,4),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(11,5),(12,5),(13,5),(15,5),(17,5),(7,6),(8,6),(10,6),(11,6),(12,6),(13,6),(15,6),(17,6),(7,7),(8,7),(9,7),(10,7),(11,7),(12,7),(15,7),(7,8),(8,8),(9,8),(10,8),(11,8),(12,8),(15,8),(3,9),(4,9),(5,9),(6,9),(7,9),(8,9),(9,9),(10,9),(11,9),(12,9),(15,9),(16,9),(17,9),(7,10),(8,10),(9,10),(10,10),(11,10),(12,10),(15,10),(16,10),(17,10),(4,11),(7,11),(8,11),(9,11),(11,11),(12,11),(15,11),(7,12),(8,12),(9,12),(11,12),(12,12),(15,12),(12,13),(15,13),(12,14),(15,14),(12,17),(13,17),(15,17),(12,18),(13,18),(15,18),(12,19),(13,19),(15,19),(12,20),(15,20),(12,21),(15,21);
/*!40000 ALTER TABLE `contest_class` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course`
--

DROP TABLE IF EXISTS `course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course` (
  `cno` int(11) NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tno` int(11) NOT NULL,
  PRIMARY KEY (`cno`),
  UNIQUE KEY `course_cno_uindex` (`cno`),
  KEY `tno` (`tno`),
  CONSTRAINT `course_ibfk_1` FOREIGN KEY (`tno`) REFERENCES `teacher` (`tno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course`
--

LOCK TABLES `course` WRITE;
/*!40000 ALTER TABLE `course` DISABLE KEYS */;
INSERT INTO `course` (`cno`, `name`, `tno`) VALUES (1,'青年大学习',2000001),(2,'ACM培训',2000002),(3,'蓝桥杯培训',2000003),(4,'深度学习入门',2000004),(5,'机器人协会迎新',2000005),(6,'CTF竞赛',2000001),(7,'每日英语单词',2000001);
/*!40000 ALTER TABLE `course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grades`
--

DROP TABLE IF EXISTS `grades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grades` (
  `GradeID` int(11) NOT NULL AUTO_INCREMENT,
  `GradeName` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`GradeID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grades`
--

LOCK TABLES `grades` WRITE;
/*!40000 ALTER TABLE `grades` DISABLE KEYS */;
INSERT INTO `grades` (`GradeID`, `GradeName`) VALUES (1,'2021级'),(2,'2022级'),(3,'2023级'),(4,'2024级');
/*!40000 ALTER TABLE `grades` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `majors`
--

DROP TABLE IF EXISTS `majors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `majors` (
  `MajorID` int(11) NOT NULL AUTO_INCREMENT,
  `MajorName` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`MajorID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `majors`
--

LOCK TABLES `majors` WRITE;
/*!40000 ALTER TABLE `majors` DISABLE KEYS */;
INSERT INTO `majors` (`MajorID`, `MajorName`) VALUES (1,'计算机科学与技术'),(2,'数字媒体技术'),(3,'软件工程'),(4,'信息安全'),(5,'物联网'),(6,'区块链');
/*!40000 ALTER TABLE `majors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `score`
--

DROP TABLE IF EXISTS `score`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `score` (
  `sno` int(11) DEFAULT NULL,
  `cno` int(11) DEFAULT NULL,
  `score` int(11) DEFAULT NULL,
  KEY `cno` (`cno`),
  KEY `sno` (`sno`),
  CONSTRAINT `score_ibfk_1` FOREIGN KEY (`sno`) REFERENCES `student` (`sno`),
  CONSTRAINT `score_ibfk_2` FOREIGN KEY (`cno`) REFERENCES `course` (`cno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `score`
--

LOCK TABLES `score` WRITE;
/*!40000 ALTER TABLE `score` DISABLE KEYS */;
/*!40000 ALTER TABLE `score` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `sno` int(11) NOT NULL,
  `request_times` int(11) DEFAULT '0' COMMENT 'requests the gpt times',
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `gender` char(2) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` char(100) COLLATE utf8mb4_unicode_ci DEFAULT '谢谢你的关注',
  `major` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT '111111',
  `study_time` int(11) DEFAULT '0' COMMENT 'study time minute',
  `ClassID` int(11) DEFAULT NULL,
  PRIMARY KEY (`sno`),
  UNIQUE KEY `student_sno_uindex` (`sno`),
  KEY `FK_ClassID` (`ClassID`),
  CONSTRAINT `FK_ClassID` FOREIGN KEY (`ClassID`) REFERENCES `classes` (`ClassID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` (`sno`, `request_times`, `name`, `gender`, `description`, `major`, `password`, `study_time`, `ClassID`) VALUES (201003001,0,'乔不思','男','热爱可抵岁月漫长','计算机22-1','111111',0,1),(201003002,0,'杨云昊','男','666','计算机22-2','111111',0,2),(201003003,0,'冷秋旱','女','谢谢你的关注','计算机22-3','111111',0,3),(2020302830,0,'郭乐天','男','谢谢你的关注','计算机22-9','111111',0,9),(2020302834,0,'刘义','男','谢谢你的关注','计算机22-9','111111',0,9),(2020304631,0,'张文帅','男','谢谢你的关注','计算机22-10','111111',0,10),(2020307201,0,'孙铭阳','男','谢谢你的关注','计算机22-10','111111',0,10),(2021305616,4,'刘阳','男','what can i say','计算机22-9','111111',0,9),(2021308502,0,'王少飞','男','谢谢你的关注','计算机22-9','111111',0,9),(2022300112,0,'张萌','男','谢谢你的关注','计算机22-9','111111',0,9),(2022300159,0,'田明阳','男','谢谢你的关注','计算机22-9','111111',0,9),(2022300166,0,'田圣旺','女','谢谢你的关注','计算机22-9','111111',0,9),(2022300363,0,'孔令众','男','谢谢你的关注','计算机22-9','111111',0,9),(2022300365,0,'李朝旭','男','谢谢你的关注','计算机22-9','111111',0,9),(2022300410,0,'潘梦婷','女','谢谢你的关注','计算机22-9','111111',0,9),(2022300483,0,'贾东阳','男','谢谢你的关注','计算机22-10','111111',0,10),(2022300534,0,'殷子建','男','谢谢你的关注','计算机22-10','111111',0,10),(2022300572,0,'王谷乔','男','谢谢你的关注','计算机22-10','111111',0,10),(2022300582,0,'朱宇扬','男','谢谢你的关注','计算机22-10','111111',0,10),(2022300942,0,'吴尊','男','谢谢你的关注','计算机22-10','111111',0,10),(2022301023,0,'王瑞','男','谢谢你的关注','计算机22-10','111111',0,10),(2022301029,0,'张德琳','男','谢谢你的关注','计算机22-10','111111',0,10),(2022301043,0,'朱缘爱','女','谢谢你的关注','计算机22-10','111111',0,10),(2022301055,0,'林文松','男','谢谢你的关注','计算机22-10','111111',0,10),(2022301091,0,'蒋成浩','男','谢谢你的关注','计算机22-10','111111',0,10),(2022301127,0,'赵许芮','女','谢谢你的关注','计算机22-10','111111',0,10),(2022301231,0,'慈欣阳','男','谢谢你的关注','计算机22-10','111111',0,10),(2022301253,0,'邓梦瑶','女','谢谢你的关注','计算机22-10','111111',0,10),(2022301309,0,'郝婷婷','女','谢谢你的关注','计算机22-10','111111',0,10),(2022301370,0,'马婧雯','女','谢谢你的关注','计算机22-9','111111',0,9),(2022301449,0,'任品蓉','女','谢谢你的关注','计算机22-9','111111',0,9),(2022301515,0,'侯向伟','男','谢谢你的关注','计算机22-9','111111',0,9),(2022301576,0,'孟子恒','男','谢谢你的关注','计算机22-9','111111',0,9),(2022301808,0,'刘隆昕','男','谢谢你的关注','计算机22-9','111111',0,9),(2022301947,0,'何云琪','男','谢谢你的关注','计算机22-9','111111',0,9),(2022302065,0,'汪同德','男','谢谢你的关注','计算机22-9','111111',0,9),(2022302669,0,'徐悦','男','谢谢你的关注','计算机22-9','111111',0,9),(2022302853,0,'徐天元','男','谢谢你的关注','计算机22-9','111111',0,9),(2022303369,0,'宋雨莲','女','谢谢你的关注','计算机22-9','111111',0,9),(2022303406,0,'张越','女','谢谢你的关注','计算机22-9','111111',0,9),(2022303632,0,'喻彪璠','男','谢谢你的关注','计算机22-10','111111',0,10),(2022303739,0,'彭皓月','男','谢谢你的关注','计算机22-10','111111',0,10),(2022303924,0,'罗献政','男','谢谢你的关注','计算机22-10','111111',0,10),(2022304138,0,'杨辉','男','谢谢你的关注','计算机22-10','111111',0,10),(2022304643,0,'章传凯','男','谢谢你的关注','计算机22-9','111111',0,9),(2022304692,0,'陶晨','女','谢谢你的关注','计算机22-9','111111',0,9),(2022304694,0,'丁钰涵','女','谢谢你的关注','计算机22-9','111111',0,9),(2022304703,0,'关硕','男','谢谢你的关注','计算机22-9','111111',0,9),(2022304758,0,'陆栋斌','男','谢谢你的关注','计算机22-9','111111',0,9),(2022304774,0,'侯新宇','女','谢谢你的关注','计算机22-9','111111',0,9),(2022304786,0,'吴鹏','男','谢谢你的关注','计算机22-9','111111',0,9),(2022304793,0,'程博文','男','谢谢你的关注','计算机22-9','111111',0,9),(2022304794,0,'洪文豪','男','谢谢你的关注','计算机22-9','111111',0,9),(2022304798,0,'王安辉','男','谢谢你的关注','计算机22-9','111111',0,9),(2022304799,11,'彭文晓','男','MAGA!','计算机22-9','111111',1,9),(2022304814,0,'倪文亭','女','谢谢你的关注','计算机22-9','111111',0,9),(2022304824,0,'潘婧文','女','谢谢你的关注','计算机22-9','111111',0,9),(2022304844,0,'石硕','男','谢谢你的关注','计算机22-9','111111',0,9),(2022304888,0,'丁钊','男','谢谢你的关注','计算机22-9','111111',0,9),(2022305164,0,'孙一硕','男','谢谢你的关注','计算机22-9','111111',0,9),(2022305413,0,'周璇','女','谢谢你的关注','计算机22-10','111111',0,10),(2022305579,0,'陈珂','女','谢谢你的关注','计算机22-10','111111',0,10),(2022305680,0,'雷丹宁','女','谢谢你的关注','计算机22-10','111111',0,10),(2022305825,0,'白史玲','女','谢谢你的关注','计算机22-10','111111',0,10),(2022306274,0,'邹淑玲','女','谢谢你的关注','计算机22-10','111111',0,10),(2022306381,0,'吴兴云','女','谢谢你的关注','计算机22-10','111111',0,10),(2022306502,0,'沈杨','男','谢谢你的关注','计算机22-10','111111',0,10),(2022306603,0,'戴海银','女','谢谢你的关注','计算机22-10','111111',0,10),(2022306658,0,'张宇昕','女','谢谢你的关注','计算机22-10','111111',0,10),(2022306815,0,'汪鑫','男','谢谢你的关注','计算机22-10','111111',0,10),(2022306868,0,'刘潇雨','女','谢谢你的关注','计算机22-10','111111',0,10),(2022306932,0,'李欣宜','女','谢谢你的关注','计算机22-10','111111',0,10),(2022307055,0,'龚晨曦','女','谢谢你的关注','计算机22-10','111111',0,10),(2022307258,0,'李梦奇','男','谢谢你的关注','计算机22-10','111111',0,10),(2022307394,0,'张玥玥','女','谢谢你的关注','计算机22-10','111111',0,10),(2022307414,0,'邵喜艳','女','谢谢你的关注','计算机22-10','111111',0,10),(2022307861,0,'陈晨','男','谢谢你的关注','计算机22-9','111111',0,9),(2022307870,0,'宋瑄皓','男','谢谢你的关注','计算机22-9','111111',0,9),(2022307874,0,'娄秀峰','男','谢谢你的关注','计算机22-9','111111',0,9),(2022307882,0,'杨博','男','谢谢你的关注','计算机22-9','111111',0,9),(2022308367,0,'王泽文','男','谢谢你的关注','计算机22-10','111111',0,10),(2022308397,0,'刘洋','男','谢谢你的关注','计算机22-10','111111',0,10),(2022308465,0,'许兴知','女','谢谢你的关注','计算机22-10','111111',0,10),(2022308479,0,'汪业斌','男','谢谢你的关注','计算机22-10','111111',0,10),(2022308502,5,'王少飞','男','谢谢你的关注','计算机22-10','111111',0,10);
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_activity_registration`
--

DROP TABLE IF EXISTS `student_activity_registration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_activity_registration` (
  `registration_id` int(11) NOT NULL AUTO_INCREMENT,
  `sno` int(11) NOT NULL,
  `activity_id` int(11) NOT NULL,
  PRIMARY KEY (`registration_id`),
  KEY `student_activity_registration_ibfk_1` (`sno`),
  KEY `student_activity_registration_ibfk_2` (`activity_id`),
  CONSTRAINT `student_activity_registration_ibfk_1` FOREIGN KEY (`sno`) REFERENCES `student` (`sno`),
  CONSTRAINT `student_activity_registration_ibfk_2` FOREIGN KEY (`activity_id`) REFERENCES `activity` (`activity_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_activity_registration`
--

LOCK TABLES `student_activity_registration` WRITE;
/*!40000 ALTER TABLE `student_activity_registration` DISABLE KEYS */;
/*!40000 ALTER TABLE `student_activity_registration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_assignment`
--

DROP TABLE IF EXISTS `student_assignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_assignment` (
  `assignment_id` int(11) NOT NULL AUTO_INCREMENT,
  `sno` int(11) NOT NULL,
  `activity_id` int(11) NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci,
  `submission_date` date NOT NULL,
  PRIMARY KEY (`assignment_id`),
  KEY `idx_sno` (`sno`),
  KEY `idx_activity_id` (`activity_id`),
  CONSTRAINT `student_assignment_ibfk_1` FOREIGN KEY (`sno`) REFERENCES `student` (`sno`),
  CONSTRAINT `student_assignment_ibfk_2` FOREIGN KEY (`activity_id`) REFERENCES `activity` (`activity_id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_assignment`
--

LOCK TABLES `student_assignment` WRITE;
/*!40000 ALTER TABLE `student_assignment` DISABLE KEYS */;
INSERT INTO `student_assignment` (`assignment_id`, `sno`, `activity_id`, `content`, `submission_date`) VALUES (19,201003001,5,'第四章 坚持以人民为中心\n2023.9.24\n一、单选题\n1.（  ）是立党为公、执政为民的本质要求。\nA.贯彻新发展理念      B.实现高质量发展\nC.为民造福            D.政治立场\n答案：C\n2.（  ）始终是党的生命线和根本工作路线，是我们党永葆青春活力和战斗力的重要传家宝。\nA.群众路线   B.经济路线   C.人民立场    D.政治立场\n答案：A\n3.（  ）是新时代坚持和发展中国特色社会主义的根本立场，是贯穿党治国理政全部项目的一条红线。\nA.把马克思主义基本原理与中国实际相结合    B.坚持以人民为中心\nC.坚持和发展中国特色社会主义              D.“五位一体”总体布局\n答案：B\n4.中国共产党区别于其他政党的显著标志是（  ）。\nA.深化改革   B.人民立场     C.促进高质量发展     D.实事求是\n答案：B\n5.（ ）是党执政的最大底气，也是党执政最深厚的根基。\nA.实现共产主义理想     B.物质基础雄厚    C.有丰富经验    D. 人民\n答案：D\n6.（  ）是党的工作的最高裁决者和最终评判者。\nA.实践     B.人民       C.国务院      D.党中央\n答案：B\n7.（  ）是贯彻群众路线的有效途径。 \nA.以人民为中心                    B. 调查研究\nC.把人民对美好生活作为奋斗目标      D.构建新发展格局\n答案：B\n8.我们党讲宗旨，讲了很多话，但说到底还是（ ）这句话。\nA.以人民为中心       B.为人民服务\nC.坚持人民主体地位   D.群众路线是根本工作路线\n答案：B\n9.新时代要坚持以人民为中心，在推动社会全面进步中促进（   ）的全面发展。\n','2024-06-03'),(22,2022304799,12,'计算机视觉代做项目，车道线分割，零售商品识别，AI小项目等等，传统视觉opencv与深度学习，图像分类，目标检测，姿态估计，实例分割，模型部署pytorch，TensorFlow框架，tensorrt框架gpu加速，openvino框架cpu加速，python与c++都可，价格可商议','2024-06-03'),(23,201003002,5,'当','2024-06-16'),(24,201003002,5,'塞特谈','2024-06-16');
/*!40000 ALTER TABLE `student_assignment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_contest_answers`
--

DROP TABLE IF EXISTS `student_contest_answers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_contest_answers` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `contest_id` int(11) NOT NULL,
  `sno` int(11) NOT NULL,
  `question_type` enum('选择题','判断题','问答题') COLLATE utf8mb4_unicode_ci NOT NULL,
  `answers` json DEFAULT NULL,
  `score` int(11) NOT NULL,
  `submission_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `unique_contest_sno` (`contest_id`,`sno`),
  KEY `sno` (`sno`),
  CONSTRAINT `student_contest_answers_ibfk_1` FOREIGN KEY (`contest_id`) REFERENCES `contest` (`contest_id`),
  CONSTRAINT `student_contest_answers_ibfk_2` FOREIGN KEY (`sno`) REFERENCES `student` (`sno`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_contest_answers`
--

LOCK TABLES `student_contest_answers` WRITE;
/*!40000 ALTER TABLE `student_contest_answers` DISABLE KEYS */;
INSERT INTO `student_contest_answers` (`id`, `contest_id`, `sno`, `question_type`, `answers`, `score`, `submission_date`) VALUES (1,3,2022304799,'选择题',NULL,5,'2024-06-05 09:09:05'),(2,5,2022304799,'判断题',NULL,10,'2024-06-05 09:15:45'),(3,6,2022304799,'问答题',NULL,5,'2024-06-05 09:24:44'),(9,4,2022304799,'选择题',NULL,5,'2024-06-05 09:52:04'),(10,7,2022308502,'问答题',NULL,20,'2024-06-05 10:27:02'),(12,7,2022304799,'问答题',NULL,25,'2024-06-05 02:32:59'),(13,8,2022304799,'选择题',NULL,20,'2024-06-05 02:37:22'),(15,9,2022304799,'判断题',NULL,15,'2024-06-05 02:46:35'),(16,10,2022304799,'选择题',NULL,45,'2024-06-05 03:45:03'),(17,11,2021305616,'判断题',NULL,50,'2024-06-05 04:45:04'),(18,5,2021305616,'判断题',NULL,15,'2024-06-06 01:39:29'),(19,11,2022304799,'判断题',NULL,55,'2024-06-06 04:17:09'),(20,8,2022308502,'选择题',NULL,5,'2024-06-06 15:35:59'),(21,11,2022308502,'判断题',NULL,5,'2024-06-06 15:36:24'),(22,9,2022308502,'判断题',NULL,5,'2024-06-06 16:09:57'),(23,6,201003002,'问答题',NULL,15,'2024-06-10 05:33:41'),(24,7,201003002,'问答题',NULL,0,'2024-06-15 18:23:44'),(25,8,201003002,'选择题',NULL,5,'2024-06-16 02:39:12'),(26,12,2022304799,'判断题',NULL,30,'2024-06-17 18:14:57'),(27,4,2021305616,'选择题',NULL,0,'2024-06-18 06:25:19');
/*!40000 ALTER TABLE `student_contest_answers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher`
--

DROP TABLE IF EXISTS `teacher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher` (
  `tno` int(11) NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`tno`),
  UNIQUE KEY `teacher_tno_uindex` (`tno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher`
--

LOCK TABLES `teacher` WRITE;
/*!40000 ALTER TABLE `teacher` DISABLE KEYS */;
INSERT INTO `teacher` (`tno`, `name`, `password`) VALUES (2000001,'蒋社想','111111'),(2000002,'冷秋旱','111111'),(2000003,'杨云昊','111111'),(2000004,'王然','000004'),(2000005,'付强','000005'),(2000006,'木木','000000'),(8888888,'乔不思','111111');
/*!40000 ALTER TABLE `teacher` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-06-30 21:44:50
