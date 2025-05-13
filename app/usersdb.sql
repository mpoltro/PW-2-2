-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: db
-- Creato il: Mag 09, 2025 alle 17:40
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
-- Database: `usersdb`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `Authenticated`
--

CREATE TABLE `Authenticated` (
  `Id` int NOT NULL,
  `Code` varchar(256) NOT NULL,
  `Uso` int NOT NULL,
  `Created_At` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `User_Id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `Badges`
--

CREATE TABLE `Badges` (
  `Id` int NOT NULL,
  `Nation` varchar(64) NOT NULL,
  `Location` varchar(128) NOT NULL,
  `Location_Name` varchar(128) NOT NULL,
  `Created_At` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Updated_At` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `User_Id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dump dei dati per la tabella `Badges`
--

INSERT INTO `Badges` (`Id`, `Nation`, `Location`, `Location_Name`, `Created_At`, `Updated_At`, `User_Id`) VALUES
(1, 'Italia', 'Bologna', 'Lepida', '2025-05-09 09:16:17', '2025-05-09 09:59:19', 1),
(4, 'Italia', 'Bologna', 'Lepida', '2025-05-09 09:18:43', '2025-05-09 09:18:43', 8),
(6, 'Italia', 'Bologna', 'Lepida', '2025-05-09 10:43:44', '2025-05-09 10:43:44', 9),
(8, 'Italia', 'Bologna', 'Lepida', '2025-05-09 10:56:31', '2025-05-09 10:56:31', 13);

-- --------------------------------------------------------

--
-- Struttura della tabella `Photos`
--

CREATE TABLE `Photos` (
  `Id` int NOT NULL,
  `Name` varchar(255) NOT NULL,
  `Path` varchar(512) DEFAULT NULL,
  `Created_At` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Updated_At` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `User_Id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dump dei dati per la tabella `Photos`
--

INSERT INTO `Photos` (`Id`, `Name`, `Created_At`, `Updated_At`, `User_Id`) VALUES
(1, '7.jpg', '2025-05-09 09:16:17', '2025-05-09 09:59:28', 1),
(4, '8.jpg', '2025-05-09 09:18:43', '2025-05-09 09:18:43', 8),
(6, '9.jpg', '2025-05-09 10:44:49', '2025-05-09 10:44:49', 9),
(8, '13.jpg', '2025-05-09 10:56:31', '2025-05-09 10:56:31', 13);

-- --------------------------------------------------------

--
-- Struttura della tabella `Users`
--

CREATE TABLE `Users` (
  `Id` int NOT NULL,
  `Email` varchar(128) NOT NULL,
  `Username` varchar(128) NOT NULL,
  `Password` varchar(256) NOT NULL,
  `Salt` varchar(128) NOT NULL,
  `Role` varchar(64) NOT NULL,
  `Created_At` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Updated_At` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dump dei dati per la tabella `Users`
--

INSERT INTO `Users` (`Id`, `Email`, `Username`, `Password`, `Salt`, `Role`, `Created_At`, `Updated_At`) VALUES
(1, 'SVieTHn1+cH9xuA4z/4newJvLBsIhhIzMnfDGrcP9jY=', 'Sconosciuto', '20ccc374ac4df89f54681a3c31494b742eed58d87ceeb3d28a0abbd39d2cb9d1', '186d49a06b918772132bdd41fef586c0ce78f85392cdff383250cbb187346a0c', 'guest', '2025-05-09 08:01:30', '2025-05-09 16:08:25'),
(3, 'TxuNVebBlPB3yQ3Y5mPssTQnRcDSBadBGoM9ynV3JCs=', 'Muzzo', 'aaadf5813902f45ad23516911153c4af7d30281e9cd5287e7779e76d2bbc2bc6', '65f18c8c5de98a0d4d41a058918f5159d1fc6efd04ec6aa1e360c3e99b6085b0', 'admin', '2025-04-17 19:12:46', '2025-05-09 17:38:47'),
(8, '1kemrORs/6uQrOUae5weE/9nRDuIEg5n0Of6HRniRPo=', 'Mattia', 'b5493b3d64884ad742a145cdbb93cd4d4745890fd383d322bbd2db49c091ba21', '916dba22b719ef4b0d708784c30fc9d7ec8dfe5d53d155740328807c517b6c26', 'admin', '2025-05-09 09:18:41', '2025-05-09 15:57:18'),
(9, 'pSdRhMwWp7sACGZBTSDts9cmFjeQDS/aBNiaab8D9+w=', 'Mene', 'e8c3783e15e18a10a7d6c1e024002ae9f8b22dc49e6aba222cc806dc1fcda311', 'd7bdf02f5b2f49f7e813e72b7545d251682fbb199e0413f9e84223661b9e75e8', 'admin', '2025-05-09 10:41:54', '2025-05-09 16:06:28'),
(13, 'x5J6y7v6IcyHBV4fQVJ+bYincsW7ObnifFRjll9dKgY=', 'Matte', 'a02591a925121f00b22b6b0099aa63380d84213c4fc7e6de8548a7214db3a0c3', '5d26548a3f4d03d444ea212014835f1d157e25118ad4e39c7eec030e563bee1d', 'admin', '2025-05-09 10:56:26', '2025-05-09 17:39:39');

-- --------------------------------------------------------

--
-- Struttura della tabella `User_Accesses`
--

CREATE TABLE `User_Accesses` (
  `Id` int NOT NULL,
  `Status` varchar(128) NOT NULL,
  `Created_At` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Updated_At` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Photo_Id` int DEFAULT NULL,
  `Badge_Id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dump dei dati per la tabella `User_Accesses`
--

INSERT INTO `User_Accesses` (`Id`, `Status`, `Created_At`, `Updated_At`, `Photo_Id`, `Badge_Id`) VALUES
(3, 'fallito', '2025-04-27 19:22:25', '2025-04-27 20:00:58', 1, 1),
(8, 'corretto', '2025-04-29 19:26:25', '2025-04-29 07:38:23', 1, 1),
(10, 'fallito', '2025-04-25 19:26:25', '2025-04-25 19:26:25', 1, 1),
(11, 'fallito', '2025-04-24 19:26:25', '2025-04-24 19:26:25', 1, 1),
(21, 'fallito', '2025-05-09 09:59:52', '2025-05-09 09:59:52', 1, 1),
(22, 'fallito', '2025-05-09 10:00:29', '2025-05-09 10:00:29', 1, 1),
(23, 'fallito', '2025-05-09 10:00:36', '2025-05-09 10:00:36', 1, 1),
(25, 'fallito', '2025-05-09 10:23:15', '2025-05-09 10:23:15', 1, 1),
(26, 'fallito', '2025-05-09 10:23:22', '2025-05-09 10:23:22', 1, 1),
(27, 'fallito', '2025-05-09 10:23:30', '2025-05-09 10:23:30', 1, 1),
(28, 'fallito', '2025-05-09 10:23:37', '2025-05-09 10:23:37', 1, 1),
(29, 'fallito', '2025-05-09 10:23:48', '2025-05-09 10:23:48', 1, 1),
(30, 'fallito', '2025-05-09 10:23:58', '2025-05-09 10:23:58', 1, 1),
(31, 'fallito', '2025-05-09 10:24:05', '2025-05-09 10:24:05', 1, 1),
(32, 'fallito', '2025-05-09 10:24:13', '2025-05-09 10:24:13', 1, 1),
(33, 'fallito', '2025-05-09 10:24:21', '2025-05-09 10:24:21', 1, 1),
(34, 'fallito', '2025-05-09 10:24:39', '2025-05-09 10:24:39', 1, 1),
(35, 'fallito', '2025-05-09 10:24:48', '2025-05-09 10:24:48', 1, 1),
(36, 'fallito', '2025-05-09 10:24:58', '2025-05-09 10:24:58', 1, 1),
(37, 'fallito', '2025-05-09 10:25:05', '2025-05-09 10:25:05', 1, 1),
(38, 'fallito', '2025-05-09 10:25:12', '2025-05-09 10:25:12', 1, 1),
(39, 'fallito', '2025-05-09 10:25:19', '2025-05-09 10:25:19', 1, 1),
(40, 'fallito', '2025-05-09 10:25:27', '2025-05-09 10:25:27', 1, 1),
(41, 'fallito', '2025-05-09 10:25:35', '2025-05-09 10:25:35', 1, 1),
(42, 'fallito', '2025-05-09 10:25:42', '2025-05-09 10:25:42', 1, 1),
(43, 'fallito', '2025-05-09 10:25:49', '2025-05-09 10:25:49', 1, 1),
(44, 'fallito', '2025-05-09 10:25:57', '2025-05-09 10:25:57', 1, 1),
(45, 'fallito', '2025-05-09 10:26:05', '2025-05-09 10:26:05', 1, 1),
(46, 'fallito', '2025-05-09 10:26:13', '2025-05-09 10:26:13', 1, 1),
(47, 'fallito', '2025-05-09 10:26:20', '2025-05-09 10:26:20', 1, 1),
(48, 'fallito', '2025-05-09 10:26:27', '2025-05-09 10:26:27', 1, 1),
(49, 'fallito', '2025-05-09 10:27:19', '2025-05-09 10:27:19', 1, 1),
(50, 'fallito', '2025-05-09 10:27:27', '2025-05-09 10:27:27', 1, 1),
(51, 'fallito', '2025-05-09 10:28:09', '2025-05-09 10:28:09', 1, 1),
(53, 'fallito', '2025-05-09 10:35:00', '2025-05-09 10:35:00', 1, 1),
(54, 'fallito', '2025-05-09 10:35:08', '2025-05-09 10:35:08', 1, 1),
(56, 'riuscito', '2025-05-09 10:56:52', '2025-05-09 10:56:52', 8, 8),
(57, 'fallito', '2025-05-09 13:46:44', '2025-05-09 13:46:44', 1, 1),
(58, 'fallito', '2025-05-09 13:46:45', '2025-05-09 13:46:45', 1, 1),
(59, 'fallito', '2025-05-09 13:47:05', '2025-05-09 13:47:05', 1, 1),
(60, 'fallito', '2025-05-09 13:47:18', '2025-05-09 13:47:18', 1, 1),
(61, 'fallito', '2025-05-09 13:47:41', '2025-05-09 13:47:41', 1, 1),
(62, 'fallito', '2025-05-09 13:48:21', '2025-05-09 13:48:21', 1, 1),
(63, 'riuscito', '2025-05-09 10:55:57', '2025-05-09 10:55:57', 6, 6),
(64, 'fallito', '2025-05-09 10:55:57', '2025-05-09 10:55:57', 6, 6);

--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `Authenticated`
--
ALTER TABLE `Authenticated`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `User_Id` (`User_Id`);

--
-- Indici per le tabelle `Badges`
--
ALTER TABLE `Badges`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `User_Id` (`User_Id`);

--
-- Indici per le tabelle `Photos`
--
ALTER TABLE `Photos`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `User_Id` (`User_Id`);

--
-- Indici per le tabelle `Users`
--
ALTER TABLE `Users`
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `Email` (`Email`),
  ADD KEY `Username` (`Username`);

--
-- Indici per le tabelle `User_Accesses`
--
ALTER TABLE `User_Accesses`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `Photo_Id` (`Photo_Id`),
  ADD KEY `Badge_Id` (`Badge_Id`);

--
-- AUTO_INCREMENT per le tabelle scaricate
--

--
-- AUTO_INCREMENT per la tabella `Authenticated`
--
ALTER TABLE `Authenticated`
  MODIFY `Id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT per la tabella `Badges`
--
ALTER TABLE `Badges`
  MODIFY `Id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT per la tabella `Photos`
--
ALTER TABLE `Photos`
  MODIFY `Id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT per la tabella `Users`
--
ALTER TABLE `Users`
  MODIFY `Id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT per la tabella `User_Accesses`
--
ALTER TABLE `User_Accesses`
  MODIFY `Id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=65;

--
-- Limiti per le tabelle scaricate
--

--
-- Limiti per la tabella `Authenticated`
--
ALTER TABLE `Authenticated`
  ADD CONSTRAINT `Authenticated_ibfk_1` FOREIGN KEY (`User_Id`) REFERENCES `Users` (`Id`) ON DELETE CASCADE;

--
-- Limiti per la tabella `Badges`
--
ALTER TABLE `Badges`
  ADD CONSTRAINT `Badges_ibfk_1` FOREIGN KEY (`User_Id`) REFERENCES `Users` (`Id`) ON DELETE CASCADE;

--
-- Limiti per la tabella `Photos`
--
ALTER TABLE `Photos`
  ADD CONSTRAINT `Photos_ibfk_1` FOREIGN KEY (`User_Id`) REFERENCES `Users` (`Id`) ON DELETE CASCADE;

--
-- Limiti per la tabella `User_Accesses`
--
ALTER TABLE `User_Accesses`
  ADD CONSTRAINT `User_Accesses_ibfk_1` FOREIGN KEY (`Photo_Id`) REFERENCES `Photos` (`Id`) ON DELETE CASCADE,
  ADD CONSTRAINT `User_Accesses_ibfk_2` FOREIGN KEY (`Badge_Id`) REFERENCES `Badges` (`Id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
