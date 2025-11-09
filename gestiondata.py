#Libreria de gestion de datos
import pandas as pd
import cn as cn


# Función para procesar los archivos.
def procesar_dataframe_ventas(df):
    try:
        # Almacenar los DataFrames de cada archivo XLSX
        dfs = []  # correctas
        dfsc = []  # canceladas
        filtrado = pd.DataFrame()  # dataset nuevo, solo columnas especificas

        # Diccionario para mapear condiciones y sus valores, para ajustar errores en grupos.        
        mapeo_condiciones_grupos = {
        "4G LTE OFICINA": "847 - GRUPO NET LTE 6",
        "4G LTE OFICINA - 10 Mbps / 2 Mbps": "847 - GRUPO NET LTE 6",
        "4G LTE OFICINA - 3 Mbps / 1.5 Mbps": "844 - GRUPO NET LTE 3",
        "ALTICE BUSINESS FIT": "830 - ACTIV-NEGOCIOS-GRUPO 5",
        "ALTICE BUSINESS FIT - ALTICE BUSINESS FIT 150": "830 - ACTIV-NEGOCIOS-GRUPO 5",
        "ALTICE BUSINESS FIT CERRADO": "829 - ACTIV-NEGOCIOS-GRUPO 4",
        "ALTICE BUSINESS FIT CERRADO - ALTICE BUSINESS FIT CERRADO": "829 - ACTIV-NEGOCIOS-GRUPO 4",
        "ALTICE BUSINESS FIT CONTROLADO": "830 - ACTIV-NEGOCIOS-GRUPO 5",
        "ALTICE BUSINESS FIT CONTROLADO - ALTICE BUSINESS FIT CONTROLADO 150": "830 - ACTIV-NEGOCIOS-GRUPO 5",
        "ALTICE CARD": "4 - CARD",
        "ALTICE CARD CANARIO": "4 - CARD",
        "ALTICE PREPAGO": "4 - CARD",
        "ALTICE PREPAGO - APPS SMALL 100 MIN / 1GB + 2GB": "884 - GRUPO 1",
        "ALTICE PREPAGO - CARD": "4 - CARD",
        "ALTICE PREPAGO REGIONAL": "4 - CARD",
        "ALTICE PREPAGO SIMO": "322 - GRUPO CARD SIM ONLY",
        "ALTICE PREPAGO SIMO - APPS LARGE 200 MIN / 4GB": "886 - GRUPO 3",
        "ALTICE PREPAGO SIMO - APPS LARGE 200 MIN / 7GB + 23GB": "887 - GRUPO 4",
        "ALTICE PREPAGO SIMO - APPS MEDIUM 100 MIN / 3GB + 12GB": "885 - GRUPO 2",
        "ALTICE PREPAGO SIMO - APPS MEDIUM 150 MIN / 2GB": "885 - GRUPO 2",
        "ALTICE PREPAGO SIMO - APPS MEDIUM 200MIN / 5GB + 20GB": "886 - GRUPO 3",
        "ALTICE PREPAGO SIMO - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
        "ALTICE PREPAGO SIMO - APPS SMALL 100 MIN / 1GB + 2GB": "884 - GRUPO 1",
        "ALTICE PREPAGO SIMO - APPS SMALL 100 MIN / 2GB + 5GB": "884 - GRUPO 1",
        "ALTICE PREPAGO SIMO - CARD": "322 - GRUPO CARD SIM ONLY",
        "ALTICE PREPAGO SIMO - PRO SMALL 200 MIN / 8GB +27GB": "888 - GRUPO 5",
        "ALTICE PREPAGO SIMO - PRO SMALL 300 MIN / 10GB + 35GB": "888 - GRUPO 5",
        "ALTICE PREPAGO SIMO - SIMO DATA": "323 - GRUPO CARD SIMO DATA",
        "ALTICE PREPAGO SIMO (DEALER)": "322 - GRUPO CARD SIM ONLY",
        "ALTICE PREPAGO SIMO REGIONAL": "323 - GRUPO CARD SIMO DATA",
        "ALTICE PREPAGO SIMO REGIONAL - APPS SMALL 100 MIN / 1GB + 2GB": "884 - GRUPO 1",
        "BUSINESS FIT": "831 - ACTIV-NEGOCIOS-GRUPO 6",
        "BUSINESS FIT CERRADO": "829 - ACTIV-NEGOCIOS-GRUPO 4",
        "BUSINESS FIT CONTROLADO": "831 - ACTIV-NEGOCIOS-GRUPO 6",
        "FLEX": "889 - GRUPO 6",
        "FLEX - APPS LARGE 200 MIN / 4GB": "886 - GRUPO 3",
        "FLEX - APPS LARGE 200 MIN / 7GB + 23GB": "887 - GRUPO 4",
        "FLEX - APPS MEDIUM 100 MIN / 3GB + 12GB": "885 - GRUPO 2",
        "FLEX - APPS MEDIUM 150 MIN / 2GB": "885 - GRUPO 2",
        "FLEX - APPS MEDIUM 200MIN / 5GB + 20GB": "886 - GRUPO 3",
        "FLEX - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
        "FLEX - APPS SMALL 100 MIN / 1GB + 2GB": "884 - GRUPO 1",
        "FLEX - APPS SMALL 100 MIN / 2GB + 5GB": "884 - GRUPO 1",
        "FLEX - APPS XLARGE 200 MIN / 5GB": "887 - GRUPO 4",
        "FLEX - CARD": "322 - GRUPO CARD SIM ONLY",
        "FLEX - PRO EXTRA LARGE 1000 MIN / 35GB": "912 - GRUPO 12",
        "FLEX - PRO EXTRA LARGE 300 MIN / 25GB +75GB": "893 - GRUPO 9",
        "FLEX - PRO EXTRA LARGE 300 MIN / 35GB": "895 - GRUPO 11",
        "FLEX - PRO EXTRA LARGE 500 MIN / 25GB +90GB": "894 - GRUPO 10",
        "FLEX - PRO EXTRA LARGE 500 MIN / 35GB": "895 - GRUPO 11",
        "FLEX - PRO LARGE 200 MIN / 20GB +45GB": "890 - GRUPO 7",
        "FLEX - PRO LARGE 200 MIN / 25GB": "893 - GRUPO 9",
        "FLEX - PRO LARGE 300 MIN / 20GB + 50GB": "891 - GRUPO 8",
        "FLEX - PRO LARGE 300 MIN / 25GB": "893 - GRUPO 9",
        "FLEX - PRO LARGE 500 MIN / 25GB": "894 - GRUPO 10",
        "FLEX - PRO MEDIUM 150 MIN / 20GB": "890 - GRUPO 7",
        "FLEX - PRO MEDIUM 200 MIN / 15GB + 35GB": "889 - GRUPO 6",
        "FLEX - PRO MEDIUM 200 MIN / 20GB": "890 - GRUPO 7",
        "FLEX - PRO MEDIUM 300 MIN / 15GB + 40GB": "889 - GRUPO 6",
        "FLEX - PRO MEDIUM 300 MIN / 20GB": "891 - GRUPO 8",
        "FLEX - PRO MEDIUM 500 MIN / 20GB": "893 - GRUPO 9",
        "FLEX - PRO SMALL 100 MIN / 10GB": "889 - GRUPO 6",
        "FLEX - PRO SMALL 200 MIN / 10GB": "889 - GRUPO 6",
        "FLEX - PRO SMALL 200 MIN / 8GB +27GB": "888 - GRUPO 5",
        "FLEX - PRO SMALL 300 MIN / 10GB": "889 - GRUPO 6",
        "FLEX - PRO SMALL 300 MIN / 10GB + 35GB": "888 - GRUPO 5",
        "FLEX - PRO SMALL 500 MIN / 10GB": "891 - GRUPO 8",
        "FLEX - PRO ULTRA 1000MIN / 30GB + 130GB": "912 - GRUPO 12",
        "FLEX - PRO ULTRA 300MIN / 30GB + 130GB": "895 - GRUPO 11",
        "FLEX - PRO ULTRA 500MIN / 30GB + 130GB": "895 - GRUPO 11",
        "FLEX - PRO XSMALL 100 MIN / 7GB": "888 - GRUPO 5",
        "FLEX ALTICE - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
        "FLEX ARDILLA": "884 - GRUPO 1",
        "FLEX ARDILLA - APPS MEDIUM 150 MIN / 2GB": "885 - GRUPO 2",
        "FLEX ARDILLA - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
        "FLEX ARDILLA - APPS SMALL 100 MIN / 2GB + 5GB": "884 - GRUPO 1",
        "FLEX ARDILLA LOS MIOS": "884 - GRUPO 1",
        "FLEX ARDILLA LOS MIOS - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
        "FLEX CANARIO": "888 - GRUPO 5",
        "FLEX CANARIO - APPS MEDIUM 200MIN / 5GB + 20GB": "886 - GRUPO 3",
        "FLEX CANARIO N/FDS": "885 - GRUPO 2",
        "FLOTILLA": "284 - ACTIV-NEGOCIOS-GRUPO 1",
        "FLOTILLA ADICIONAL": "284 - ACTIV-NEGOCIOS-GRUPO 1",
        "FLOTILLA ALTICE BUSINESS": "285 - ACTIV-NEGOCIOS-GRUPO 2",
        "FLOTILLA ALTICE BUSINESS ADICIONAL": "284 - ACTIV-NEGOCIOS-GRUPO 1",
        "FLOTILLA ALTICE BUSINESS FLEX": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "FLOTILLA ALTICE BUSINESS FLEX ADICIONAL": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "FLOTILLA FM": "284 - ACTIV-NEGOCIOS-GRUPO 1",
        "FLOTILLA FM ADICIONAL": "284 - ACTIV-NEGOCIOS-GRUPO 1",
        "FLOTILLA FM GRUPO": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "FLOTILLA FM GRUPO ADICIONAL": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "FLOTILLA NET ADICIONAL": "284 - ACTIV-NEGOCIOS-GRUPO 1",
        "FLOTILLA NET ALTICE BUSINESS": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "FLOTILLA NET ALTICE BUSINESS ADICIONAL": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "FLOTILLA NET FM": "284 - ACTIV-NEGOCIOS-GRUPO 1",
        "FLOTILLA NET FM ADICIONAL": "285 - ACTIV-NEGOCIOS-GRUPO 2",
        "FLOTILLA NET FM GRUPO": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "FLOTILLA NET FM GRUPO ADICIONAL": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "INDIVIDUAL": "830 - ACTIV-NEGOCIOS-GRUPO 5",
        "INDIVIDUAL CERRADO": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "INDIVIDUAL CONTROLADO": "829 - ACTIV-NEGOCIOS-GRUPO 4",
        "INTERNET ALTICE-F": "802 - GRUPO NET 6 - 18 MESES",
        "INTERNET ALTICE-F - 10GB BEST EFFORT ESPECIAL": "467 - GRUPO NET 4 - 18 MESES",
        "INTERNET ALTICE-F - 15GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
        "INTERNET ALTICE-F - 20GB BEST EFFORT": "802 - GRUPO NET 6 - 18 MESES",
        "INTERNET ALTICE-F - 25GB BEST EFFORT": "803 - GRUPO NET 7 - 18 MESES",
        "INTERNET ALTICE-F - 3GB REGIONAL BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "INTERNET ALTICE-F - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
        "INTERNET ALTICE-F - 7GB BEST EFFORT": "466 - GRUPO NET 3 - 18 MESES",
        "INTERNET ALTICE-F REGIONAL": "464 - GRUPO NET 1 - 18 MESES",
        "INTERNET ALTICE-F REGIONAL - 10GB BEST EFFORT ESPECIAL": "467 - GRUPO NET 4 - 18 MESES",
        "INTERNET ALTICE-F REGIONAL - 15GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
        "INTERNET ALTICE-F REGIONAL - 3GB REGIONAL BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "INTERNET ALTICE-F REGIONAL - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
        "INTERNET ALTICE-F REGIONAL - 7GB BEST EFFORT": "466 - GRUPO NET 3 - 18 MESES",
        "INTERNET ALTICE-M": "471 - GRUPO NET 5 - 18 MESES",
        "INTERNET ALTICE-M - 10GB BEST EFFORT ESPECIAL": "467 - GRUPO NET 4 - 18 MESES",
        "INTERNET ALTICE-M - 15GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
        "INTERNET ALTICE-M - 20GB BEST EFFORT": "802 - GRUPO NET 6 - 18 MESES",
        "INTERNET ALTICE-M - 25GB BEST EFFORT": "803 - GRUPO NET 7 - 18 MESES",
        "INTERNET ALTICE-M - 3GB REGIONAL BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "INTERNET ALTICE-M - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
        "INTERNET ALTICE-M - 7GB BEST EFFORT": "466 - GRUPO NET 3 - 18 MESES",
        "INTERNET ALTICE-M REGIONAL": "465 - GRUPO NET 2 - 18 MESES",
        "INTERNET ALTICE-M REGIONAL - 10GB BEST EFFORT ESPECIAL": "467 - GRUPO NET 4 - 18 MESES",
        "INTERNET ALTICE-M REGIONAL - 3GB REGIONAL BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "INTERNET ALTICE-M REGIONAL - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
        "INTERNET ALTICE-M REGIONAL - 7GB BEST EFFORT": "466 - GRUPO NET 3 - 18 MESES",
        "INTERNET MBB - INTERNET MBB 1 + 2GB": "972 - GRUPO MBB 0 - 36 MESES",
        "INTERNET MOVIL ALTICE": "471 - GRUPO NET 5 - 18 MESES",
        "INTERNET MOVIL ALTICE - 15GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
        "INTERNET MOVIL ALTICE - 20GB BEST EFFORT": "802 - GRUPO NET 6 - 18 MESES",
        "INTERNET MOVIL ESTUDIANTES": "804 - GRUPO NET 0 - 12 MESES (EST)",        
        "INTERNET MOVIL PREPAGO - ALTICE TRAVEL PACK": "482 - GRUPO NET 0 - 12 MESES",
        "INTERNET MOVIL PREPAGO - PAQUETE 2GB X 15 DIAS A $599": "482 - GRUPO NET 0 - 12 MESES",
        "INTERNET MOVIL PREPAGO - Paquete Internet móvil prepago": "482 - GRUPO NET 0 - 12 MESES",
        "INTERNET NEGOCIOS ALTICE-F": "477 - GRUPO NET 4 - 18 MESES (NEG)",
        "INTERNET NEGOCIOS ALTICE-M": "477 - GRUPO NET 4 - 18 MESES (NEG)",
        "M2M CONTROL": "242 - Altice NET DATA PRE PAGO",        
        "MAX - APPS LARGE 200 MIN / 4GB": "886 - GRUPO 3",
        "MAX - APPS LARGE 200 MIN / 7GB + 23GB": "887 - GRUPO 4",
        "MAX - APPS MEDIUM 100 MIN / 3GB + 12GB": "885 - GRUPO 2",
        "MAX - APPS MEDIUM 150 MIN / 2GB": "885 - GRUPO 2",
        "MAX - APPS MEDIUM 200MIN / 5GB + 20GB": "886 - GRUPO 3",
        "MAX - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
        "MAX - APPS SMALL 100 MIN / 1GB + 2GB": "884 - GRUPO 1",
        "MAX - APPS SMALL 100 MIN / 2GB + 5GB": "884 - GRUPO 1",
        "MAX - APPS XLARGE 200 MIN / 5GB": "887 - GRUPO 4",
        "MAX - PRO EXTRA LARGE 1000 MIN / 35GB": "912 - GRUPO 12",
        "MAX - PRO EXTRA LARGE 300 MIN / 25GB +75GB": "893 - GRUPO 9",
        "MAX - PRO EXTRA LARGE 300 MIN / 35GB": "895 - GRUPO 11",
        "MAX - PRO EXTRA LARGE 500 MIN / 25GB +90GB": "894 - GRUPO 10",
        "MAX - PRO EXTRA LARGE 500 MIN / 35GB": "895 - GRUPO 11",
        "MAX - PRO LARGE 200 MIN / 20GB +45GB": "890 - GRUPO 7",
        "MAX - PRO LARGE 200 MIN / 25GB": "893 - GRUPO 9",
        "MAX - PRO LARGE 300 MIN / 20GB + 50GB": "891 - GRUPO 8",
        "MAX - PRO LARGE 300 MIN / 25GB": "893 - GRUPO 9",
        "MAX - PRO LARGE 500 MIN / 25GB": "894 - GRUPO 10",
        "MAX - PRO MEDIUM 150 MIN / 20GB": "890 - GRUPO 7",
        "MAX - PRO MEDIUM 200 MIN / 15GB + 35GB": "889 - GRUPO 6",
        "MAX - PRO MEDIUM 200 MIN / 20GB": "890 - GRUPO 7",
        "MAX - PRO MEDIUM 300 MIN / 15GB + 40GB": "889 - GRUPO 6",
        "MAX - PRO MEDIUM 300 MIN / 20GB": "891 - GRUPO 8",
        "MAX - PRO MEDIUM 500 MIN / 20GB": "893 - GRUPO 9",
        "MAX - PRO SMALL 100 MIN / 10GB": "889 - GRUPO 6",
        "MAX - PRO SMALL 200 MIN / 10GB": "889 - GRUPO 6",
        "MAX - PRO SMALL 200 MIN / 8GB +27GB": "888 - GRUPO 5",
        "MAX - PRO SMALL 300 MIN / 10GB": "889 - GRUPO 6",
        "MAX - PRO SMALL 300 MIN / 10GB + 35GB": "888 - GRUPO 5",
        "MAX - PRO SMALL 500 MIN / 10GB": "891 - GRUPO 8",
        "MAX - PRO ULTRA 1000MIN / 30GB + 130GB": "912 - GRUPO 12",
        "MAX - PRO ULTRA 300MIN / 30GB + 130GB": "895 - GRUPO 11",
        "MAX - PRO ULTRA 500MIN / 30GB + 130GB": "895 - GRUPO 11",
        "MAX - PRO XSMALL 100 MIN / 7GB": "888 - GRUPO 5",
        "MAX CANARIO": "885 - GRUPO 2",
        "MAX CANARIO - PRO XSMALL 100 MIN / 7GB": "888 - GRUPO 5",
        "MAX LEOPARDO": "893 - GRUPO 9",
        "NUEVO BUSINESS FIT": "830 - ACTIV-NEGOCIOS-GRUPO 5",
        "NUEVO BUSINESS FIT CERRADO": "829 - ACTIV-NEGOCIOS-GRUPO 4",
        "NUEVO BUSINESS FIT CONTROLADO": "833 - ACTIV-NEGOCIOS-GRUPO 8",
        "NUEVO INTERNET ALTICE-M": "802 - GRUPO NET 6 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - 10GB BEST EFFORT ESPECIAL": "467 - GRUPO NET 4 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - 15GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - 20GB BEST EFFORT": "802 - GRUPO NET 6 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - 25GB BEST EFFORT": "803 - GRUPO NET 7 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - 3GB REGIONAL BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - 7GB BEST EFFORT": "466 - GRUPO NET 3 - 18 MESES",
        "PLAN 200MIN/10GB + BONO 5GB - INDOTEL": "830 - ACTIV-NEGOCIOS-GRUPO 5",
        "RT - FLEX BASICO": "883 - GRUPO 0",
        "RT - FLEX BASICO - APPS LARGE 200 MIN / 4GB": "886 - GRUPO 3",
        "RT - FLEX BASICO - APPS LARGE 200 MIN / 7GB + 23GB": "887 - GRUPO 4",
        "RT - FLEX BASICO - APPS MEDIUM 100 MIN / 3GB + 12GB": "885 - GRUPO 2",
        "RT - FLEX BASICO - APPS MEDIUM 150 MIN / 2GB": "885 - GRUPO 2",
        "RT - FLEX BASICO - APPS MEDIUM 200MIN / 5GB + 20GB": "886 - GRUPO 3",
        "RT - FLEX BASICO - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
        "RT - FLEX BASICO - APPS SMALL 100 MIN / 1GB + 2GB": "884 - GRUPO 1",
        "RT - FLEX BASICO - APPS SMALL 100 MIN / 2GB + 5GB": "884 - GRUPO 1",
        "RT - FLEX BASICO - PRO MEDIUM 200 MIN / 15GB + 35GB": "889 - GRUPO 6",
        "RT - FLEX BASICO - PRO SMALL 200 MIN / 8GB +27GB": "888 - GRUPO 5",
        "RT - FLEX BASICO - PRO XSMALL 100 MIN / 7GB": "888 - GRUPO 5",
        "RT - INTERNET ALTICE- F": "464 - GRUPO NET 1 - 18 MESES",
        "RT - INTERNET ALTICE- F - 10GB BEST EFFORT ESPECIAL": "467 - GRUPO NET 4 - 18 MESES",
        "RT - INTERNET ALTICE- F - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
        "RT - INTERNET ALTICE- M": "464 - GRUPO NET 1 - 18 MESES",
        "RT - INTERNET ALTICE- M - 15GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
        "RT - INTERNET ALTICE- M - 3GB REGIONAL BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "RT - INTERNET ALTICE- M - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
        "RT - INTERNET ALTICE- M - 7GB BEST EFFORT": "466 - GRUPO NET 3 - 18 MESES",
        "STAFF ALTICE": "6 - STAFF",
        "INTERNET MOVIL ALTICE - 1MBPS/1MBPS MOVIL": "464 - GRUPO NET 1 - 18 MESES",
        "RT - INTERNET ALTICE- F - 2GB BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "RT - INTERNET ALTICE- M - 2GB BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "INTERNET ALTICE-F - 10GB BEST EFFORT": "467 - GRUPO NET 4 - 18 MESES",
        "INTERNET MOVIL ESTUDIANTES - VELOCIDAD 10MBPS/256KBPS": "467 - GRUPO NET 4 - 18 MESES",
        "INTERNET MOVIL ALTICE - 3MBPS/1.5MBPS MOVIL": "471 - GRUPO NET 5 - 18 MESES",
        "INTERNET ALTICE-M - 10GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - NEW INTERNET ALTICE 6GB": "465 - GRUPO NET 2 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - NEW INTERNET ALTICE 8GB": "466 - GRUPO NET 3 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - NEW INTERNET ALTICE 12GB": "467 - GRUPO NET 4 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - NEW INTERNET ALTICE 18GB": "471 - GRUPO NET 5 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - NEW INTERNET ALTICE 22GB": "802 - GRUPO NET 6 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - NEW INTERNET ALTICE 30GB": "803 - GRUPO NET 7 - 18 MESES",
        "FLEX - BASICO 70MIN / 70MB": "883 - GRUPO 0",
        "FLEX - BASICO 60MIN / 30MB": "883 - GRUPO 0",
        "FLEX ARDILLA - ARDILLA 60 MIN + 60 SMS (FLEX)": "883 - GRUPO 0",
        "FLEX ARDILLA LOS MIOS - ARDILLA 30 MIN + 30 MIN (FLEX)": "883 - GRUPO 0",
        "RT - FLEX BASICO - BASICO 50MIN /1GB": "883 - GRUPO 0",
        "RT - FLEX BASICO - BASICO 50MIN": "883 - GRUPO 0",
        "RT - FLEX BASICO - BASICO 60MIN / 30MB": "883 - GRUPO 0",
        "RT - FLEX BASICO - BASICO 60MIN / 2GB": "883 - GRUPO 0",
        "FLEX - APPS 100 MINUTOS/1GB": "884 - GRUPO 1",
        "FLEX - APPS 75 MINUTOS/700MB": "884 - GRUPO 1",
        "FLEX - APPS XSMALL 100 MIN / 100MB": "884 - GRUPO 1",
        "FLEX - PLAN APPS 100MIN/100MB": "884 - GRUPO 1",
        "FLEX - APPS SMALL 150 MIN / 250MB": "885 - GRUPO 2",
        "FLEX - BASICO150MIN / 100MB": "885 - GRUPO 2",
        "FLEX - PLAN APPS 200MIN/100MB": "885 - GRUPO 2",
        "FLEX - APPS ESPECIAL DE 200 MIN / 4GB": "886 - GRUPO 3",
        "FLEX - APPS MEDIUM 200 MIN / 700MB": "886 - GRUPO 3",
        "FLEX - BASICO250MIN / 500MB": "886 - GRUPO 3",
        "FLEX - PLAN APPS PLUS 100MIN/500MB": "886 - GRUPO 3",
        "FLEX - PLAN APPS PLUS 200MIN/500MB": "886 - GRUPO 3",
        "MAX - APPS MEDIUM 200 MIN / 700MB": "886 - GRUPO 3",
        "FLEX - APPS MEDIUM 200 MIN / 5GB + 20GB": "886 - GRUPO 3",
        "FLEX - APPS LARGE 200 MIN / 1GB": "887 - GRUPO 4",
        "FLEX - BASICO 300MIN / 1GB": "887 - GRUPO 4",
        "FLEX - PLAN APPS FULL 100MIN/1GB": "887 - GRUPO 4",
        "FLEX - APPS LARGE 250 MIN / 2GB": "888 - GRUPO 5",
        "FLEX - PLAN APPS FULL 200MIN/1GB": "888 - GRUPO 5",
        "FLEX - PRO ESPECIAL DE 100 MIN / 7GB": "888 - GRUPO 5",
        "FLEX - PRO XSMALL 100 MIN / 2GB": "888 - GRUPO 5",
        "MAX - PRO XSMALL 100 MIN / 2GB": "888 - GRUPO 5",
        "FLEX - PRO SMALL 100 MIN / 4GB": "889 - GRUPO 6",
        "FLEX - PRO SMALL 200 MIN / 4GB": "889 - GRUPO 6",
        "MAX - PRO SMALL 200 MIN / 4GB": "889 - GRUPO 6",
        "MAX - PLAN PRO 100MIN/5GB": "889 - GRUPO 6",
        "MAX - PRO SMALL 300 MIN / 4GB": "889 - GRUPO 6",
        "FLEX - PRO MEDIUM 150 MIN / 7GB": "890 - GRUPO 7",
        "FLEX - PRO MEDIUM 200 MIN / 7GB": "890 - GRUPO 7",
        "MAX - PRO MEDIUM 200 MIN / 7GB": "890 - GRUPO 7",
        "FLEX - PRO MEDIUM 300 MIN / 7GB": "891 - GRUPO 8",
        "FLEX - PRO SMALL 500 MIN / 4GB": "891 - GRUPO 8",
        "MAX - PRO MEDIUM 300 MIN / 7GB": "891 - GRUPO 8",
        "FLEX - PRO LARGE 200 MIN / 14GB": "893 - GRUPO 9",
        "MAX - PRO MEDIUM 500 MIN / 7GB": "893 - GRUPO 9",
        "FLEX - PRO LARGE 300 MIN / 14GB": "893 - GRUPO 9",
        "MAX - PRO LARGE 300 MIN / 14GB": "893 - GRUPO 9",
        "MAX - PRO LARGE 200 MIN / 14GB + 50GB": "893 - GRUPO 9",
        "MAX - PRO LARGE 200 MIN / 14GB": "893 - GRUPO 9",
        "FLEX - PRO LARGE 500 MIN / 14GB": "894 - GRUPO 10",
        "MAX - PRO LARGE 500 MIN / 14GB": "894 - GRUPO 10",
        "MAX - PRO EXTRA LARGE 1000 MIN / 25GB": "912 - GRUPO 12",        
        "FLEX - APPS SMALL 100 MIN / 1GB + 2GB BONO":"884 - GRUPO 1",
        "RT - FLEX BASICO - APPS SMALL 100 MIN / 1GB + 2GB BONO":"884 - GRUPO 1",
        "FLEX - APPS SMALL 100 MIN / 2GB + 5GB BONO":"884 - GRUPO 1",
        "FLEX - APPS MEDIUM 100 MIN / 3GB + 12GB BONO":"885 - GRUPO 2",
        "FLEX - APPS MEDIUM 200MIN / 5GB + 20GB BONO":"886 - GRUPO 3",
        "RT - FLEX BASICO - APPS MEDIUM 200MIN / 5GB + 20GB BONO":"	886 - GRUPO 3",
        "FLEX - APPS LARGE 200 MIN / 7GB + 23GB BONO":"887 - GRUPO 4",
        "FLEX - PRO SMALL 200 MIN / 8GB +27GB BONO":"888 - GRUPO 5",
        "FLEX - PRO SMALL 300 MIN / 10GB + 35GB BONO":"888 - GRUPO 5",
        "MAX - PRO SMALL 300 MIN / 10GB + 35GB BONO":"888 - GRUPO 5",
        "FLEX - PRO MEDIUM 200 MIN / 15GB + 35GB BONO":"889 - GRUPO 6",
        "FLEX - PRO MEDIUM 300 MIN / 15GB + 40GB BONO":"889 - GRUPO 6",
        "FLEX - PRO LARGE 200 MIN / 20GB +45GB BONO":"890 - GRUPO 7",
        "FLEX - PRO LARGE 300 MIN / 20GB + 50GB BONO":"891 - GRUPO 8",
        "MAX - PRO EXTRA LARGE 300 MIN / 25GB +75GB BONO":"893 - GRUPO 9",
        "FLEX - PRO EXTRA LARGE 500 MIN / 25GB +90GB BONO":"894 - GRUPO 10",
        "FLEX - APPS MEDIUM 200MIN / 5GB + 20GB BONO":"886 - GRUPO 3",
        "FLEX - APPS MEDIUM 100 MIN / 3GB + 12GB BONO":"885 - GRUPO 2",
        "FLEX - PRO EXTRA LARGE 300 MIN / 25GB +75GB BONO":"893 - GRUPO 9",   
        "MAX - APPS SMALL 100 MIN / 2GB + 5GB BONO":"884 - GRUPO 1",
        "MAX - PRO SMALL 200 MIN / 8GB +27GB BONO":"888 - GRUPO 5",
        "MAX - PRO LARGE 300 MIN / 20GB + 50GB BONO":"891 - GRUPO 8",
        }

        mapeo_negocios_grupos = {
            "284 - ACTIV-NEGOCIOS-GRUPO 1":"884 - GRUPO 1",
            "285 - ACTIV-NEGOCIOS-GRUPO 2":"885 - GRUPO 2",
            "286 - ACTIV-NEGOCIOS-GRUPO 3":"886 - GRUPO 3",
            "829 - ACTIV-NEGOCIOS-GRUPO 4":"887 - GRUPO 4",
            "830 - ACTIV-NEGOCIOS-GRUPO 5":"888 - GRUPO 5",
            "831 - ACTIV-NEGOCIOS-GRUPO 6":"889 - GRUPO 6",
            "290 - ACTIV-NEGOCIOS-GRUPO 7":"890 - GRUPO 7",
            "833 - ACTIV-NEGOCIOS-GRUPO 8":"891 - GRUPO 8",
            "292 - ACTIV-NEGOCIOS-GRUPO 9":"893 - GRUPO 9",
            "293 - ACTIV-NEGOCIOS-GRUPO 10":"894 - GRUPO 10",
            "294 - ACTIV-NEGOCIOS-GRUPO 11":"895 - GRUPO 11",
            "295 - ACTIV-NEGOCIOS-GRUPO 12":"912 - GRUPO 12",
            "477 - GRUPO NET 4 - 18 MESES (NEG)":"467 - GRUPO NET 4 - 18 MESES",
            "474 - GRUPO NET 5 NEGOCIOS - 18 MESES":"471 - GRUPO NET 5 - 18 MESES",

        }

        mapeo_condiciones_ventacosto = {
            "1325 - VENTA DE EQUIPOS AL COSTO": "0"            
        }   
    
        mapeo_condiciones_Up_Down = {
            "5000 - AUMENTO DE PLAN CON VENTA EQUIPO POR REEMPLAZO":"0",
            "5001 - AUMENTO DE PLAN CON VENTA EQUIPO POR FIDE":"0",
            "5030 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR REEMPLAZO":"0",
            "5031 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR FIDE":"0",
        }

        try:
            # Convertir la columna 'fecha_digitacion_orden' a datetime y establecer la hora a las 00:00:00
            df["fecha_digitacion_orden"] = pd.to_datetime(
                df["fecha_digitacion_orden"], errors="coerce"
            ).dt.normalize()

            # Eliminar filas con fechas no válidas
            df = df.dropna(subset=["fecha_digitacion_orden"])

            # Rellenar valores nulos
            df = df.fillna("null")

            #Limpiar espacios en los nombres de las columnas de planes
            if 'nom_plan' in df.columns:
                df['nom_plan'] = df['nom_plan'].str.strip()
            if 'nom_plan_anterior' in df.columns:
                df['nom_plan_anterior'] = df['nom_plan_anterior'].str.strip()

            # Normalizar columnas numéricas, truncando decimales para asegurar conversión a entero.
            for col in ['telefono', 'imei', 'id_transaccion', 'sim','tel_contacto','tel_contacto2']:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)

            # Función para modificar la columna según la condición, y aplicar el grupo correcto.
            def modificar_valor(row: pd.Series) -> str | None:
                return mapeo_condiciones_grupos.get(
                    row["nom_plan_anterior"], row["grupo_activacion_anterior"]
                )

            def modificar_ventacosto(row):
                return mapeo_condiciones_ventacosto.get(
                    row["razon_servicio"], row["grupo_activacion_orden"]
                )

            def modificar_grupo(row):
                return mapeo_negocios_grupos.get(
                    row["grupo_activacion_orden"], row["grupo_activacion_orden"]
                )

            def modificar_UpDown(row):
                return mapeo_condiciones_Up_Down.get(
                    row["razon_servicio"], row["grupo_activacion_anterior"]
                )

            # Aplicar la función a las columnas que se desean modificar
            df["grupo_activacion_anterior"] = df.apply(modificar_valor, axis=1) # type: ignore
            df["grupo_activacion_anterior"] = df.apply(modificar_UpDown, axis=1) # type: ignore
            df["grupo_activacion_orden"] = df.apply(modificar_ventacosto, axis=1) # type: ignore
            df["grupo_activacion_orden"] = df.apply(modificar_grupo, axis=1) # type: ignore

            # Lista de condiciones para eliminar filas y limpiar datos innecesarios.
            condiciones_usuario = ["OS - SISTEMA ORDENES(AUTOMATICO)"]
            condiciones_razon_servicio = [
                "1159 - MISCELANEOS VIDEO ON DEMAND",
                "1309 - ACTIVACIONES Y DESACTIVACIÓN SERVICIOS OPCIONALES",
                "1304 - USO DE FIDEPUNTOS (HABLA MAS / P&S)",
                "1312 - TRANSFERENCIA FIDEPUNTOS",
                "1315 - CAMBIO DE NUMERO",
                "1365 - CAMBIO DE NUMERO (PORTABILIDAD)",
                "1369 - RECONEXION POR ROBO / PÉRDIDA",
                "1372 - SEPARACION DE CUENTAS",
                "1400 - TRASPASO DE CONTRATO  PREPAGO",
                "1376 - UNIFICACION DE CUENTAS",
                "1318 - DISMINUCION PRODUCTO POSTPAGO-PREPAGO",
                "1352 - SUSPENSION TEMPORAL (90 DIAS)",
                "1331 - POR ERROR DE DIGITACIÓN",
                "1368 - RECONEXIÓN DE SERVICIO",
                "1327 - A SOLICITUD DEL CLIENTE",
                "1351 - SUSPENSION TEMPORAL (60 DIAS)",
                "1329 - SUSPENSIÓN DE SERVICIO POR PÉRDIDA O ROBO",
                "349 - RETIRO QUITESE",
                "5020 - TITULAR CON VALIDADOR DE IDENTIDAD",
                "1323 - DISMINUCIÓN DE PLAN / PAQUETE",
            ]

            condiciones_canceladas = ["Cancelada"]

            # Seleccionar filas canceladas
            canceladas = df["estado_transaccion"].isin(condiciones_canceladas)
            dfsc.append(df[canceladas])

            # Crear una condición compuesta para eliminar filas y datos innecesarios
            condicion = (
                (df["usuario_creo_orden"].isin(condiciones_usuario))
                | (df["razon_servicio"].isin(condiciones_razon_servicio))
                | (df["estado_transaccion"].isin(condiciones_canceladas))
            )

            # Eliminar las filas que cumplen la condición
            df.drop(df[condicion].index, inplace=True)

            # Añadir el DataFrame resultante a la lista
            dfs.append(df)

        except Exception as e:
            print(f"Error al procesar el dataframe: {e}")

        # Unificar los DataFrames en uno solo
        if dfs:
            try:
                data_set = pd.concat(dfs, ignore_index=True)
                data_set_c = pd.concat(dfsc, ignore_index=True)

                columnas_valida = [
                    "id_transaccion",
                    "fecha_digitacion_orden",
                    "fecha_termino_orden",
                    "estado_transaccion",
                    "usuario_creo_orden",
                    "entity_code",
                    "subcanal",
                    "tipo_actividad",
                    "razon_servicio",
                    "telefono",
                    "imei",
                    "nom_plan",
                    "nom_plan_anterior",
                    "grupo_activacion_orden",
                    "grupo_activacion_anterior",
                ]

                # Filtrar las columnas de interés
                filtrado = data_set[columnas_valida].copy()

                # Convertir columnas relevantes a numericas para evitar errores en comparaciones
                columnas_a_convertir = ["id_transaccion", "telefono", "imei"]
                for columna in columnas_a_convertir:
                    if columna in filtrado.columns:
                        filtrado.loc[:, columna] = pd.to_numeric(
                            filtrado[columna], errors="coerce"
                        )
                    else:
                        print(f"Advertencia: La columna '{columna}' no está en el DataFrame.")
                       

                # Eliminar duplicados
                filtrado = filtrado.drop_duplicates(
                    subset=["id_transaccion", "razon_servicio", "telefono", "imei"],
                    keep="last",
                )                
                

                # Guardar en tabla transacciones
                cn.guardar_filtrado_en_db(filtrado)   
                generar_ventas();    

                # Mostrar mensaje de confirmación
                print("Procesamiento completadoo y datos guardados en la base de datos.")                

            except Exception as e:
                print(f"Error al procesar los datos: {e}")
                
        else:
            print("No se encontraron archivos válidos para procesar.")
            
    except Exception as e:
        print(f"Error al procesar los datos: {e}")        

def generar_ventas():
    """
    Genera un reporte de ventas basado en los datos almacenados en la base de datos.
    Agrupa las ventas por diferentes categorías y guarda el resultado en la base de datos.
    """
    try:
        conn = cn.conect()
        query = """
        SELECT *FROM transacciones
        """
        query2 = """
        SELECT codigo, supervisor FROM usuarios
        """
        query3 = """
        SELECT *FROM incentivosEmpleados
        """
        data = pd.read_sql(query, conn)
        data_supers = pd.read_sql(query2, conn)
        data_incentivos = pd.read_sql(query3, conn)        

        # Convertir la columna 'fecha_digitacion_orden' a datetime y establecer la hora a las 00:00:00
        data["fecha_digitacion_orden"] = pd.to_datetime(
            data["fecha_digitacion_orden"], errors="coerce"
        ).dt.normalize() 

        # Convertir los datos en un DataFrame
        df_group = data.copy()
        df_group_Intermet = data.copy()
        df_group_Card = data.copy()

        # Definir los grupos de ventas y sus condiciones
        grupos_ventas = {
            "Flex/Max": (
                df_group["razon_servicio"].isin(
                    [
                        "1425 - ACTIVACIONES DE LINEAS - SIN EQUIPOS (DEALERS)",
                        "1409 - PORT SIN NUMERO TEMPORERO/SIN EQUIPO (CANAL PRESE)",
                        "1126 - ACTIVACIONES DE LÍNEAS - CON EQUIPOS (EFECTIVO)",
                        "1301 - ACTIVACIONES DE LINEAS - CON EQUIPOS",
                        "1302 - PORT IN CON NUMERO TEMPORERO/CON EQUIPO",
                        "1349 - PORT CON NUMERO TEMPORERO/SIN EQUIPO (CANAL PRESE)",
                        "1402 - ACTIVACIONES LÍNEAS-SIN EQUIPOS (CANAL PRESENCIAL)",
                    ]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Migraciones": (
                df_group["razon_servicio"].isin(
                    [
                        "1468 - AUMENTO DE PRODUCTO CON VENTA DE EQUIPO",                        
                        "1316 - AUMENTO DE PRODUCTO PREPAGO-POSTPAGO",                        
                    ]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Fidepuntos Pospago": (
                df_group["razon_servicio"].isin(
                    ["1378 - USO DE FIDEPUNTOS (CAMBIA TU MOVIL)"]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Fidepuntos Aumento": (
                df_group["razon_servicio"].isin(
                    [
                     "5001 - AUMENTO DE PLAN CON VENTA EQUIPO POR FIDE",
                     "5201 - AUMENTO DE PRODUCTO CON VENTA EQUIPO POR FIDE",
                     ]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Fidepuntos Disminucion": (
                df_group["razon_servicio"].isin(
                    ["5031 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR FIDE"]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Reemplazo Pospago": (
                df_group["razon_servicio"].isin(["1324 - VENTA DE EQUIPOS/REEMPLAZO"])
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Reemplazo Aumento": (
                df_group["razon_servicio"].isin(
                    [
                     "5000 - AUMENTO DE PLAN CON VENTA EQUIPO POR REEMPLAZO",
                     "5200 - AUMENTO DE PRODUCTO CON VENTA EQUIPO POR REEMPLAZO",
                     ]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Reemplazo Disminucion": (
                df_group["razon_servicio"].isin(
                    ["5030 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR REEMPLAZO"]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
            "Aumentos Pospago": (
                df_group["razon_servicio"].isin(["1322 - AUMENTO DE PLAN / PAQUETE"])
                & df_group["grupo_activacion_orden"].str.contains(
                    r"883 - GRUPO 0|884 - GRUPO 1|885 - GRUPO 2|886 - GRUPO 3|887 - GRUPO 4|"
                    r"888 - GRUPO 5|889 - GRUPO 6|890 - GRUPO 7|891 - GRUPO 8|893 - GRUPO 9|"
                    r"894 - GRUPO 10|895 - GRUPO 11|912 - GRUPO 12",
                    case=False,
                    na=False,
                )
            ),
        }

        grupos_ventas_internet = {
            "Internet": (
                df_group_Intermet["razon_servicio"].isin(
                    [
                        "1301 - ACTIVACIONES DE LINEAS - CON EQUIPOS",
                        "1402 - ACTIVACIONES LÍNEAS-SIN EQUIPOS (CANAL PRESENCIAL)",
                    ]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "InternetCard": (
                df_group_Intermet["razon_servicio"].isin(
                    [
                        "1301 - ACTIVACIONES DE LINEAS - CON EQUIPOS",
                        "1402 - ACTIVACIONES LÍNEAS-SIN EQUIPOS (CANAL PRESENCIAL)",
                    ]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"482 - GRUPO NET 0 - 12 MESES",
                    case=False,
                    na=False,
                )
            ),
            "Migracion Internet": (
                df_group_Intermet["razon_servicio"].isin(
                    [
                        "1468 - AUMENTO DE PRODUCTO CON VENTA DE EQUIPO",
                        "1316 - AUMENTO DE PRODUCTO PREPAGO-POSTPAGO",
                    ]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "Reemplazo Internet": (
                df_group_Intermet["razon_servicio"].isin(
                    ["1324 - VENTA DE EQUIPOS/REEMPLAZO"]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "Reemplazo InternetAum": (
                df_group_Intermet["razon_servicio"].isin(
                    ["5000 - AUMENTO DE PLAN CON VENTA EQUIPO POR REEMPLAZO"]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "Reemplazo InternetDism": (
                df_group_Intermet["razon_servicio"].isin(
                    ["5030 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR REEMPLAZO"]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "Fidepuntos Internet": (
                df_group_Intermet["razon_servicio"].isin(
                    ["1378 - USO DE FIDEPUNTOS (CAMBIA TU MOVIL)"]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "Fidepuntos InternetAum": (
                df_group_Intermet["razon_servicio"].isin(
                    ["5001 - AUMENTO DE PLAN CON VENTA EQUIPO POR FIDE"]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GR UPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "Fidepuntos InternetDism": (
                df_group_Intermet["razon_servicio"].isin(
                    ["5031 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR FIDE"]
                )
                & df_group_Intermet["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
            "Aumentos Internet": (
                df_group_Intermet["razon_servicio"].isin(
                    ["1322 - AUMENTO DE PLAN / PAQUETE"]
                )
                & df_group["grupo_activacion_orden"].str.contains(
                    r"464 - GRUPO NET 1 - 18 MESES|465 - GRUPO NET 2 - 18 MESES|466 - GRUPO NET 3 - 18 MESES|"
                    r"467 - GRUPO NET 4 - 18 MESES|471 - GRUPO NET 5 - 18 MESES|802 - GRUPO NET 6 - 18 MESES|"
                    r"803 - GRUPO NET 7 - 18 MESES|",
                    case=False,
                    na=False,
                )
            ),
        }

        grupos_ventas_card = {
            "Card": (
                df_group_Card["razon_servicio"].isin(
                    [
                        "1425 - ACTIVACIONES DE LINEAS - SIN EQUIPOS (DEALERS)",
                        "1409 - PORT SIN NUMERO TEMPORERO/SIN EQUIPO (CANAL PRESE)",                        
                        "1349 - PORT CON NUMERO TEMPORERO/SIN EQUIPO (CANAL PRESE)",
                        "1402 - ACTIVACIONES LÍNEAS-SIN EQUIPOS (CANAL PRESENCIAL)",
                    ]
                )
                & df_group_Card["grupo_activacion_orden"].str.contains(
                    r"322 - GRUPO CARD SIM ONLY|4 - CARD",
                    case=False,
                    na=False,
                )
            ),
            "CardEquipo": (
                df_group_Card["razon_servicio"].isin(
                    [
                        "1126 - ACTIVACIONES DE LÍNEAS - CON EQUIPOS (EFECTIVO)",
                        "1301 - ACTIVACIONES DE LINEAS - CON EQUIPOS",
                        "1302 - PORT IN CON NUMERO TEMPORERO/CON EQUIPO",                        
                    ]
                )
                & df_group_Card["grupo_activacion_orden"].str.contains(
                    r"322 - GRUPO CARD SIM ONLY|4 - CARD",
                    case=False,
                    na=False,
                )
            ),
        }

        # Agrupación card
        df_group_Card["tipo_venta"] = None
        for tipo, condicion in grupos_ventas_card.items():
            df_group_Card.loc[condicion, "tipo_venta"] = tipo

        # Extraer Grupo a partir de dos patrones
        df_group_Card["Grupo1"] = df_group_Card["grupo_activacion_orden"].str.extract(
            r"(\d+) - GRUPO CARD SIM ONLY", expand=False
        )
        df_group_Card["Grupo2"] = df_group_Card["grupo_activacion_orden"].str.extract(
            r"(\d+) - CARD", expand=False
        )

        df_group_Card["Grupo"] = df_group_Card["Grupo1"].fillna(df_group_Card["Grupo2"])
        df_group_Card.drop(["Grupo1", "Grupo2"], axis=1, inplace=True)
        # fin card

        # Agrupación Flex/Max
        df_group["tipo_venta"] = None
        for tipo, condicion in grupos_ventas.items():
            df_group.loc[condicion, "tipo_venta"] = tipo

        # Extraer el número del grupo para agruparlo
        df_group["Grupo"] = (
            df_group["grupo_activacion_orden"]
            .str.extract(r"GRUPO (\d+)", expand=True)
            .bfill(axis=1)[0]
        )        

        # Extraer el número del grupo anterior para agruparlo
        df_group["Grupo_Anterior"] = (
            df_group["grupo_activacion_anterior"]
            .str.extract(r"GRUPO (\d+)", expand=True)
            .bfill(axis=1)[0]
        )
        # fin flex/mas

        # Agrupación Internet
        df_group_Intermet["tipo_venta"] = None
        for tipo, condicion in grupos_ventas_internet.items():
            df_group_Intermet.loc[condicion, "tipo_venta"] = tipo

        # Extraer el número del grupo para agruparlo
        df_group_Intermet["Grupo"] = (
            df_group_Intermet["grupo_activacion_orden"]
            .str.extract(r"GRUPO NET (\d+)", expand=True)
            .bfill(axis=1)[0]
        )

        # Extraer el número del grupo anterior para agruparlo
        df_group_Intermet["Grupo_Anterior"] = (
            df_group_Intermet["grupo_activacion_anterior"]
            .str.extract(r"GRUPO NET (\d+)", expand=True)
            .bfill(axis=1)[0]
        )

        df_group_Intermet["Grupo_Anterior"] = df_group_Intermet["Grupo_Anterior"].fillna(0)
        # Fin Agrupacion Internet

        # Rellenar NaN en "Grupo Anterior" con 0
        df_group["Grupo_Anterior"] = df_group["Grupo_Anterior"].fillna(0)

        # Generar conteo
        ventas_validas = df_group.dropna(subset=["tipo_venta", "Grupo"], how="any")
        conteo_ventas = (
            ventas_validas.groupby(
                [
                    "entity_code",
                    "subcanal",
                    "fecha_digitacion_orden",                    
                    "usuario_creo_orden",                    
                    "tipo_venta",
                    "Grupo",
                    "Grupo_Anterior",
                ]
            )
            .size()
            .reset_index()
        )

        # Internet
        ventas_validas_internet = df_group_Intermet.dropna(
            subset=["tipo_venta", "Grupo"], how="any"
        )
        conteo_ventas_internet = (
            ventas_validas_internet.groupby(
                [
                    "entity_code",
                    "subcanal",
                    "fecha_digitacion_orden",                                        
                    "usuario_creo_orden",
                    "tipo_venta",
                    "Grupo",
                    "Grupo_Anterior",
                ]
            )
            .size()
            .reset_index()
        )

        # card
        ventas_validas_card = df_group_Card.dropna(subset=["tipo_venta"], how="any")
        conteo_ventas_card = (
            ventas_validas_card.groupby(
                [
                    "entity_code",
                    "subcanal",
                    "fecha_digitacion_orden",                                       
                    "usuario_creo_orden",
                    "tipo_venta",
                    "Grupo",
                ]
            )
            .size()
            .reset_index()
        )

        # Renombrar la columna de conteo
        conteo_ventas.rename(columns={0: "total_ventas"}, inplace=True)
        conteo_ventas_internet.rename(columns={0: "total_ventas"}, inplace=True)
        conteo_ventas_card.rename(columns={0: "total_ventas"}, inplace=True)

        # Verificar si los DataFrames están vacíos
        if conteo_ventas.empty:
            raise ValueError("No se encontraron ventas válidas.")

        if conteo_ventas_internet.empty:
            raise ValueError("No se encontraron ventas válidas.")

        if conteo_ventas_card.empty:
            raise ValueError("No se encontraron ventas válidas.")

        # Preparar los resultados individuales
        resultado = conteo_ventas.reset_index()
        resultado_card = conteo_ventas_card.reset_index()
        resultado_internet = conteo_ventas_internet.reset_index()

        # Concatenar todos los resultados
        reultado_final = pd.concat(
            [resultado, resultado_internet, resultado_card], ignore_index=True
        )
        reultado_final.rename(columns={"fecha_digitacion_orden": "fecha"}, inplace=True)

        # Rellenar valores nulos en Grupo_Anterior
        reultado_final["Grupo_Anterior"] = reultado_final["Grupo_Anterior"].fillna(0)        

        # Extraer código de usuario para asignar supervisores
        reultado_final["codigo"] = reultado_final["usuario_creo_orden"].str[:7]
        data_supers["codigo"] = data_supers['codigo'].astype(str)        

        # Unir con datos de supervisores
        df_combinado = pd.merge(reultado_final, data_supers, on="codigo", how="left")
        df_combinado = df_combinado.fillna(0)

        # Convertir supervisor a entero sin decimales
        df_combinado["supervisor"] = pd.to_numeric(df_combinado["supervisor"], errors='coerce')
        df_combinado["supervisor"] = df_combinado["supervisor"].fillna(0).astype(int).astype(str)

        # Lista de tipos de venta para los que Grupo_Anterior debe ser 0
        tipos_venta_grupo_anterior_cero = [
            "Reemplazo InternetAum",
            "Fidepuntos InternetDism",
            "Fidepuntos InternetAum",
            "Reemplazo InternetDism",
            "Reemplazo Disminucion",
            "Reemplazo Aumento",
            "Fidepuntos Disminucion",
            "Fidepuntos Aumento",
            "Migraciones",
        ]

        # Establecer Grupo_Anterior a 0 para los tipos de venta especificados
        df_combinado.loc[df_combinado['tipo_venta'].isin(tipos_venta_grupo_anterior_cero), 'Grupo_Anterior'] = 0

        # Reorganizar columnas
        columnas = df_combinado.columns.tolist()
        columnas.insert(
            columnas.index("usuario_creo_orden"),
            columnas.pop(columnas.index("supervisor")),
        )
        df_combinado = df_combinado[columnas]
        df_combinado.drop("codigo", axis=1, inplace=True)

        # Asegurar compatibilidad de tipos para el merge con incentivos
        df_combinado["Grupo"] = df_combinado["Grupo"].astype(str)
        df_combinado["Grupo_Anterior"] = df_combinado["Grupo_Anterior"].astype(str)
        df_combinado["tipo_venta"] = df_combinado["tipo_venta"].astype(str)

        data_incentivos["Grupo"] = data_incentivos["Grupo"].astype(str)
        data_incentivos["Grupo_Anterior"] = data_incentivos["Grupo_Anterior"].astype(str)
        data_incentivos["tipo_venta"] = data_incentivos["tipo_venta"].astype(str)

        # depuración para verificar claves de unión
        """
        print("Valores únicos en df_combinado:")
        print(f"tipo_venta: {df_combinado['tipo_venta'].unique()}")
        print(f"Grupo: {df_combinado['Grupo'].unique()}")
        print(f"Grupo_Anterior: {df_combinado['Grupo_Anterior'].unique()}")

        print("\nValores únicos en data_incentivos:")
        print(f"tipo_venta: {data_incentivos['tipo_venta'].unique()}")
        print(f"Grupo: {data_incentivos['Grupo'].unique()}")
        print(f"Grupo_Anterior: {data_incentivos['Grupo_Anterior'].unique()}")
        """

        # Realizar la unión con tabla de incentivos
        df_combinado = pd.merge(
            df_combinado,
            data_incentivos,
            on=["tipo_venta", "Grupo", "Grupo_Anterior"],
            how="left"
        )

        # Verificar registros sin coincidencia
        sin_coincidencia = df_combinado[df_combinado["Comision_100"].isna()]
        if not sin_coincidencia.empty:
            print(f"Hay {len(sin_coincidencia)} registros sin coincidencia en incentivos")
            print(sin_coincidencia[["tipo_venta", "Grupo", "Grupo_Anterior"]].head())

        # Convertir comisiones a numérico y rellenar valores nulos
        df_combinado["Comision_100"] = pd.to_numeric(df_combinado["Comision_100"], errors='coerce').fillna(0)
        df_combinado["Comision_75"] = pd.to_numeric(df_combinado["Comision_75"], errors='coerce').fillna(0)

        # Asegurar que total_ventas es numérico
        df_combinado["total_ventas"] = pd.to_numeric(df_combinado["total_ventas"], errors="coerce").fillna(0)

        # Calcular comisiones
        df_combinado["Comision_100"] = df_combinado["total_ventas"] * df_combinado["Comision_100"]
        df_combinado["Comision_75"] = df_combinado["total_ventas"] * df_combinado["Comision_75"]

        # Verificar cálculos
        print("\nEjemplos de cálculos de comisión:")
        muestra = df_combinado[df_combinado["Comision_100"] > 0].head(3)
        for _, row in muestra.iterrows():
            print(f"Venta: {row['total_ventas']}, Comisión 100%: {row['Comision_100']}")

        # Guardar en base de datos
        cn.guardar_ventas_detalle_en_db(df_combinado)
        print("Ventas generadas y guardadas en la base de datos correctamente.")      
        
    except Exception as e:
        print(f"Ocurrió un error: {e}")  
        # Fin agugacion ventas





