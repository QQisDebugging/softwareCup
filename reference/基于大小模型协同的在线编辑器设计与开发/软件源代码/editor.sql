/*
 Navicat Premium Data Transfer

 Source Server         : local
 Source Server Type    : MySQL
 Source Server Version : 50724
 Source Host           : 127.0.0.1:3306
 Source Schema         : editor

 Target Server Type    : MySQL
 Target Server Version : 50724
 File Encoding         : 65001

 Date: 01/07/2024 15:19:56
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for document
-- ----------------------------
DROP TABLE IF EXISTS `document`;
CREATE TABLE `document`  (
  `number` varchar(255) CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL,
  `name` varchar(255) CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL,
  `context` text CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL,
  `userNumber` varchar(255) CHARACTER SET gbk COLLATE gbk_chinese_ci NULL DEFAULT NULL,
  PRIMARY KEY (`number`) USING BTREE,
  INDEX `userNumber`(`userNumber`) USING BTREE,
  CONSTRAINT `document_ibfk_1` FOREIGN KEY (`userNumber`) REFERENCES `user` (`number`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = gbk COLLATE = gbk_chinese_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of document
-- ----------------------------
INSERT INTO `document` VALUES ('121', '你的第一个文档', '{\\rtf1\\ansiHello!\\parThis is some {\\b bold} text.\\par}', '6434');

-- ----------------------------
-- Table structure for publicdocument
-- ----------------------------
DROP TABLE IF EXISTS `publicdocument`;
CREATE TABLE `publicdocument`  (
  `number` varchar(255) CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL,
  `name` varchar(255) CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL,
  `context` text CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL,
  PRIMARY KEY (`number`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = gbk COLLATE = gbk_chinese_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of publicdocument
-- ----------------------------

-- ----------------------------
-- Table structure for template
-- ----------------------------
DROP TABLE IF EXISTS `template`;
CREATE TABLE `template`  (
  `number` varchar(255) CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL,
  `name` varchar(255) CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL,
  `form` text CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL,
  PRIMARY KEY (`number`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = gbk COLLATE = gbk_chinese_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of template
-- ----------------------------

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `number` varchar(255) CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL,
  `name` varchar(255) CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL,
  `pass` varchar(255) CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL,
  `member` varchar(255) CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL,
  PRIMARY KEY (`number`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = gbk COLLATE = gbk_chinese_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES ('6434', '卫东', 'weidong', '是');

-- ----------------------------
-- Table structure for usertemplate
-- ----------------------------
DROP TABLE IF EXISTS `usertemplate`;
CREATE TABLE `usertemplate`  (
  `user_number` varchar(255) CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL,
  `template_number` varchar(255) CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL,
  PRIMARY KEY (`user_number`, `template_number`) USING BTREE,
  INDEX `template_number`(`template_number`) USING BTREE,
  CONSTRAINT `usertemplate_ibfk_1` FOREIGN KEY (`user_number`) REFERENCES `user` (`number`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `usertemplate_ibfk_2` FOREIGN KEY (`template_number`) REFERENCES `template` (`number`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = gbk COLLATE = gbk_chinese_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of usertemplate
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
