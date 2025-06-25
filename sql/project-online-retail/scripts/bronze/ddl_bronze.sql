/*
===============================================================================
DDL Script: Create Bronze Tables
===============================================================================
Script Purpose:
    This script creates tables in the 'bronze' schema, dropping existing tables 
    if they already exist.
	  Run this script to re-define the DDL structure of 'bronze' Tables
===============================================================================
*/

USE [OnlineRetail];

IF OBJECT_ID('bronze.online_retail', 'U') IS NOT NULL
    DROP TABLE bronze.online_retail;
GO

CREATE TABLE bronze.online_retail (
	invoice_no		VARCHAR(10),	-- Handles 6-digit numbers & optional 'C' prefix
	stock_code		VARCHAR(10),	-- Also nominal, even if mostly numeric
	description		TEXT,			-- Free-text product description
	quantity		INT,			-- Integer quantity (can be negative for returns)
	invoice_date	DATETIME,		-- Stores date and time together
	unit_price		DECIMAL(10, 2),	-- Up to 99999999.99 in GBP (£)
	customer_id		INT,			-- 5-digit integer
	country			NVARCHAR(50)	-- Country name
);
GO
