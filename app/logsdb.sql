-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: db1
-- Creato il: Mag 04, 2025 alle 15:18
-- Versione del server: 8.4.5
-- Versione PHP: 8.2.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `logsdb`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `Access_Events`
--

CREATE TABLE `Access_Events` (
  `Id` int NOT NULL,
  `Status` enum('autorizzato','negato','sospetto') NOT NULL,
  `IP_Address` varchar(128) NOT NULL,
  `Device_Info` varchar(256) NOT NULL,
  `Location` varchar(256) NOT NULL,
  `API_Check` tinyint(1) NOT NULL,
  `Created_At` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `User_Id` int NOT NULL,
  `Country` varchar(128) DEFAULT NULL,
  `CountryCode` char(2) DEFAULT NULL,
  `Region` varchar(128) DEFAULT NULL,
  `RegionName` varchar(128) DEFAULT NULL,
  `City` varchar(128) DEFAULT NULL,
  `Latitude` decimal(10,6) DEFAULT NULL,
  `Longitude` decimal(10,6) DEFAULT NULL,
  `Timezone` varchar(64) DEFAULT NULL,
  `ISP` varchar(128) DEFAULT NULL,
  `AS_Organization` varchar(256) DEFAULT NULL,
  `Query` varchar(128) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `Errors`
--

CREATE TABLE `Errors` (
  `Id` int NOT NULL,
  `Description` text NOT NULL,
  `Action` varchar(256) NOT NULL,
  `Date_Time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `User_Id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `Logs`
--

CREATE TABLE `Logs` (
  `Id` int NOT NULL,
  `Username` varchar(128) NOT NULL,
  `Event_Type` varchar(64) NOT NULL,
  `Status_Code` int NOT NULL,
  `Date_Time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `IP_Address` varchar(128) NOT NULL,
  `Device_Info` varchar(256) NOT NULL,
  `Location` varchar(256) NOT NULL,
  `API_Response` text,
  `User_Id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `Success`
--

CREATE TABLE `Success` (
  `Id` int NOT NULL,
  `Description` text NOT NULL,
  `Action` varchar(256) NOT NULL,
  `Date_Time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `User_Id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `Warnings`
--

CREATE TABLE `Warnings` (
  `Id` int NOT NULL,
  `Description` text NOT NULL,
  `Action` varchar(256) NOT NULL,
  `Date_Time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `User_Id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `Access_Events`
--
ALTER TABLE `Access_Events`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `User_Id` (`User_Id`);

--
-- Indici per le tabelle `Errors`
--
ALTER TABLE `Errors`
  ADD PRIMARY KEY (`Id`);

--
-- Indici per le tabelle `Logs`
--
ALTER TABLE `Logs`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `User_Id` (`User_Id`),
  ADD KEY `Username` (`Username`);

--
-- Indici per le tabelle `Success`
--
ALTER TABLE `Success`
  ADD PRIMARY KEY (`Id`);

--
-- Indici per le tabelle `Warnings`
--
ALTER TABLE `Warnings`
  ADD PRIMARY KEY (`Id`);

--
-- AUTO_INCREMENT per le tabelle scaricate
--

--
-- AUTO_INCREMENT per la tabella `Access_Events`
--
ALTER TABLE `Access_Events`
  MODIFY `Id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `Errors`
--
ALTER TABLE `Errors`
  MODIFY `Id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT per la tabella `Logs`
--
ALTER TABLE `Logs`
  MODIFY `Id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `Success`
--
ALTER TABLE `Success`
  MODIFY `Id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `Warnings`
--
ALTER TABLE `Warnings`
  MODIFY `Id` int NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
