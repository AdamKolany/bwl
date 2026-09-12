--
-- PostgreSQL database dump
--

\restrict Ry6QC1EByOdEW4EQPiA2rbQ3lQFoP2EYYCfdTD1AViOmTvidgEBAXIdZ72J3hlS

-- Dumped from database version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: antworte; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.antworte (
    antwort character varying(2048),
    frage_id smallint,
    richtig character(1),
    antwort_id smallint DEFAULT nextval('public.antwortseq'::regclass) NOT NULL,
    antwort_text text,
    antwort_latex text,
    antwort_mathjson jsonb,
    hint character varying(16)
);


--
-- Name: fragen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fragen (
    frage character varying(1024),
    status character(1),
    frage_id smallint DEFAULT nextval('public.frageseq'::regclass) NOT NULL,
    "kap_kürzel" character(5),
    "th_kürzel" character(5)
);


--
-- Name: kapitel; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.kapitel (
    kapitel character varying(128),
    "kap_kürzel" character varying(5)
);


--
-- Name: themen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.themen (
    thema character varying(1024),
    "th_kürzel" character varying(5) NOT NULL,
    kapitel character varying(5),
    blocked character(1)
);


--
-- Name: kapitel_themen; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.kapitel_themen AS
 SELECT k.kapitel,
    k."kap_kürzel",
    t.thema,
    t."th_kürzel"
   FROM (public.kapitel k
     LEFT JOIN public.themen t ON (((t.kapitel)::text = (k."kap_kürzel")::text)))
  WHERE (t.blocked = 'N'::bpchar);


--
-- Name: kapitel_themen_fragen; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.kapitel_themen_fragen AS
 SELECT kt.kapitel,
    kt."kap_kürzel",
    kt.thema,
    kt."th_kürzel",
    f.frage,
    f.status,
    f.frage_id
   FROM (public.kapitel_themen kt
     LEFT JOIN public.fragen f ON ((((kt."th_kürzel")::bpchar = f."th_kürzel") AND ((kt."kap_kürzel")::bpchar = f."kap_kürzel"))));


--
-- Data for Name: antworte; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.antworte (antwort, frage_id, richtig, antwort_id, antwort_text, antwort_latex, antwort_mathjson, hint) FROM stdin;
\N	2	J	2	\N	-4\\cdot e^{4x}\\cdot \\sin(e^{4x})	\N	f'(x)= 
\N	3	J	3	\N	(2x-7)\\cdot e^{x^2-7x}	\N	f'(x)= 
\N	4	J	4	\N	\\frac{x}{\\sqrt{x^2+3}}	\N	f'(x)= 
\N	5	J	5	\N	\\frac{2x\\cdot (x-3)-(x^2+5)}{(x-3)^2}	\N	f'(x)= 
\N	7	J	7	\N	10x\\cdot \\cos(5x^2)+\\frac1x	\N	f'(x)= 
\N	8	J	8	\N	6\\cdot e^{6x}\\cdot \\sin(x)+e^{6x}\\cdot \\cos(x)	\N	f'(x)= 
\N	10	J	10	\N	(2x-7)\\cdot e^{x^2-7x}	\N	f'(x)= 
\N	11	J	11	\N	(2x-9)\\cdot e^{x^2-9x}	\N	f'(x)= 
\N	12	J	12	\N	(2x-5)\\cdot e^{x^2-5x}	\N	f'(x)= 
\N	14	J	14	\N	(2x-13)\\cdot e^{x^2-13x}	\N	f'(x)= 
\N	16	J	16	\N	6x\\cdot (x^2+2x-3)	\N	\\mathcal{A}= 
\N	17	J	17	\N	(x-2)^2	\N	\\mathcal{A}= 
\N	18	J	18	\N	(x-3)\\cdot (x+3)	\N	\\mathcal{A}= 
\N	19	J	19	\N	(x-5)^2	\N	\\mathcal{A}= 
\N	20	J	20	\N	8x\\cdot (x^2+2x-3)	\N	\\mathcal{A}= 
\N	22	J	22	\N	(x-3)\\cdot (x+3)	\N	\\mathcal{A}= 
\N	24	J	24	\N	4x\\cdot (x^2+2x-3)	\N	\\mathcal{A}= 
\N	25	J	25	\N	(3 x+4 y)\\cdot (y+z)	\N	\\mathcal{A}= 
\N	26	J	26	\N	(x-1)\\cdot (x+1)	\N	\\mathcal{A}= 
\N	27	J	27	\N	(x-4)\\cdot (x+4)	\N	\\mathcal{A}= 
\N	28	J	28	\N	(5 x-12 y)^2	\N	\\mathcal{A}= 
\N	29	J	29	\N	(x-2)\\cdot (x+2)	\N	\\mathcal{A}= 
\N	30	J	30	\N	10x\\cdot (x^2+2x-3)	\N	\\mathcal{A}= 
\N	31	J	31	\N	x^3+12x^2+48x+64	\N	\\mathcal{A}= 
\N	34	J	34	\N	x^2+14x+40	\N	\\mathcal{A}= 
\N	35	J	35	\N	x^3+12x^2+48x+64	\N	\\mathcal{A}= 
\N	36	J	36	\N	x^2+5x-50	\N	\\mathcal{A}= 
\N	37	J	37	\N	x^2+9x+8	\N	\\mathcal{A}= 
\N	38	J	38	\N	9x^2+36x+36	\N	\\mathcal{A}= 
\N	39	J	39	\N	9x^2+12x+4	\N	\\mathcal{A}= 
\N	40	J	40	\N	9x^2+36x+36	\N	\\mathcal{A}= 
\N	41	J	41	\N	x^3+15x^2+75x+125	\N	\\mathcal{A}= 
\N	42	J	42	\N	x^3+15x^2+75x+125	\N	\\mathcal{A}= 
\N	43	J	43	\N	x^3+12x^2+48x+64	\N	\\mathcal{A}= 
\N	44	J	44	\N	x^4-4	\N	\\mathcal{A}= 
\N	45	J	45	\N	x^2+2x-8	\N	\\mathcal{A}= 
\N	56	J	56	\N	\\frac{2x^2}{x^2-1}	\N	\\mathcal{W}= 
\N	64	J	64	\N	\\frac{(x-10)\\cdot (4 x+10)}{x-20}	\N	\\mathcal{W}= 
\N	65	J	65	\N	\\frac{(x+1)\\cdot (x^2-3)}{2x+12}	\N	\\mathcal{W}= 
\N	66	J	66	\N	\\frac{(x-13)\\cdot (3 x+13)}{x-23}	\N	\\mathcal{W}= 
\N	67	J	67	\N	\\frac{(x-4)\\cdot (4 x+4)}{x-10}	\N	\\mathcal{W}= 
\N	68	J	68	\N	\\frac{3\\cdot (x+10)}{2x+10}	\N	\\mathcal{W}= 
\N	69	J	69	\N	\\frac{(x+1)\\cdot (x^2-2)}{2x+16}	\N	\\mathcal{W}= 
\N	70	J	70	\N	\\frac{(x-4)\\cdot (4 x+4)}{x-18}	\N	\\mathcal{W}= 
\N	71	J	71	\N	\\frac{x\\cdot (x+4)}{x+4}	\N	\\mathcal{W}= 
\N	91	J	91	\N	\\ln x-2	\N	F(x)= 
\N	93	J	93	\N	x^2	\N	F(x)= 
\N	94	J	94	\N	e^{6x}-1	\N	F(x)= 
\N	97	J	97	\N	\\ln x-2	\N	F(x)= 
\N	99	J	99	\N	\\sin(7x)-3	\N	F(x)= 
\N	100	J	100	\N	e^{7x}-2	\N	F(x)= 
\N	103	J	103	\N	\\sin(3 x)-2	\N	F(x)= 
\N	105	J	105	\N	\\ln(x^2+4)-\\ln(4)	\N	F(x)= 
\N	6	J	6	\N	\\frac{2x}{x^2+6}-2\\cdot \\sin(2 x)	\N	f'(x)= 
\N	21	J	21	\N	4\\cdot(x+3 y)\\cdot (y+z)	\N	\\mathcal{A}= 
\N	23	J	23	\N	( x-2 y)^2	\N	\\mathcal{A}= 
\N	108	J	108	\N	x^7-\\sin(x)+C	\N	I= 
	106	J	106	\N	I=\\ln(x^2+7)+C	\N	I= 
	107	J	107	\N	\\frac13(x^2+1)^{\\frac32}+C	\N	I= 
	1	J	1	\N	\\frac{2x\\cdot (x-5)-(x^2+2)}{(x-5)^2}	\N	f'(x)= 
\N	109	J	109	\N	\\frac13(x^2+11)^{\\frac32}+C	\N	I= 
\N	110	J	110	\N	e^{8x}+C	\N	I= 
\N	111	J	111	\N	\\ln(x^2+1)+C	\N	I= 
\N	112	J	112	\N	-\\frac12\\cos(2 x)+C	\N	I= 
\N	113	J	113	\N	-\\frac18\\cos(8 x)+C	\N	I= 
\N	114	J	114	\N	x^2-\\sin(x)+C	\N	I= 
\N	115	J	115	\N	\\frac16\\sin(6 x-13)+C	\N	I= 
\N	116	J	116	\N	\\ln x+C	\N	I= 
\N	117	J	117	\N	\\frac13(x^2+3)^{\\frac32}+C	\N	I= 
\N	118	J	118	\N	\\frac15\\sin(5 x-9)+C	\N	I= 
\N	119	J	119	\N	\\frac13(x^2+13)^{\\frac32}+C	\N	I= 
\N	120	J	120	\N	e^{7x}+C	\N	I= 
\N	92	J	92	\N	x^6+3	\N	F(x)= 
\N	95	J	95	\N	x^2+1	\N	F(x)= 
\N	96	J	96	\N	\\ln(x^2+7)+1-\\ln(7)	\N	F(x)= 
\N	98	J	98	\N	\\ln x+2	\N	F(x)= 
\N	101	J	101	\N	x^3+2	\N	F(x)= 
\N	102	J	102	\N	x^3+1	\N	F(x)= 
\N	104	J	104	\N	\\sin(6 x)+1	\N	F(x)= 
\N	13	J	13	\N	2 x\\cdot \\ln x+x	\N	f'(x)= 
\N	9	J	9	\N	\\frac{2x}{x^2+7}-\\sin(x)	\N	f'(x)= 
\N	15	J	15	\N	-e^{x}\\cdot \\sin(e^{x})	\N	f'(x)= 
\N	32	J	32	\N	x^2-16y^2	\N	\\mathcal{A}= 
\N	33	J	33	\N	x^2-xy-12y^2	\N	\\mathcal{A}= 
\N	46	J	46	\N	\\frac{11x+25}{x^2+5x}	\N	\\mathcal{W}= 
\N	48	J	48	\N	\\frac{x^2+x+2}{x^2-4}	\N	\\mathcal{W}= 
\N	47	J	47	\N	\\frac{x^2+1}{x^2-1}	\N	\\mathcal{W}= 
\N	49	J	49	\N	\\frac{10x+36}{x^2+6x}	\N	\\mathcal{W}= 
\N	51	J	51	\N	\\frac{2x}{x^2-16}	\N	\\mathcal{W}= 
\N	50	J	50	\N	\\frac{13x+25}{x^2+5x}	\N	\\mathcal{W}= 
\N	54	J	54	\N	\\frac{15x+25}{x^2+5x}	\N	\\mathcal{W}= 
\N	57	J	57	\N	\\frac{2x}{x^2-9}	\N	\\mathcal{W}= 
\N	58	J	58	\N	\\frac{2x}{x^2-16}	\N	\\mathcal{W}= 
\N	59	J	59	\N	\\frac{12x+16}{x^2+4x}	\N	\\mathcal{W}= 
\N	60	J	60	\N	\\frac{14x+16}{x^2+4x}	\N	\\mathcal{W}= 
\N	61	J	61	\N	\\frac{5x+30}{2x+6}	\N	\\mathcal{W}= 
\N	62	J	62	\N	\\frac{3x+12}{2x+4}	\N	\\mathcal{W}= 
\N	63	J	63	\N	\\frac{x^3+x^2-x-1}{2x+12}	\N	\\mathcal{W}= 
\N	72	J	72	\N	\\frac{(x-10)\\cdot (1 x+10)}{x-22}	\N	\\mathcal{W}= 
\N	73	J	73	\N	\\frac{(x+1)\\cdot (x^2-1)}{2x+8}	\N	\\mathcal{W}= 
\N	74	J	74	\N	\\frac{(x+1)\\cdot (x^2-5)}{2x+12}	\N	\\mathcal{W}= 
\N	75	J	75	\N	\\frac{(x-10)\\cdot (2 x+10)}{x-22}	\N	\\mathcal{W}= 
\N	153	J	153	\N	4x^2-3x+21	\N	Q(x)= 
\N	154	J	154	\N	3x^2+9x+6	\N	Q(x)= 
\N	156	J	156	\N	2x^2+3x+6	\N	Q(x)= 
\N	157	J	157	\N	2x^2+6x+21	\N	Q(x)= 
\N	158	J	158	\N	2x^2+16	\N	Q(x)= 
\N	159	J	159	\N	-x+13	\N	R(x)= 
\N	160	J	160	\N	-x+10	\N	R(x)= 
\N	161	J	161	\N	9x+16	\N	R(x)= 
\N	162	J	162	\N	x+10	\N	R(x)= 
\N	163	J	163	\N	5x+7	\N	R(x)= 
\N	164	J	164	\N	7x+19	\N	R(x)= 
\N	165	J	165	\N	7x+10	\N	R(x)= 
	152	J	152	\N	x^2+6x+11	\N	Q(x)= 
	155	J	155	\N	2x^2+12x+6	\N	Q(x)= 
	151	J	151	\N	2x^2+3x+16	\N	Q(x)= 
\.


--
-- Data for Name: fragen; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.fragen (frage, status, frage_id, "kap_kürzel", "th_kürzel") FROM stdin;
Klammern Sie das folgende aus: \\[\\mathcal{A}=6x^3+12x^2-18x\\]	F	16	TSTA 	auskl
Klammern Sie das folgende aus: \\[\\mathcal{A}=x^2-4x+4\\]	F	17	TSTA 	auskl
Klammern Sie das folgende aus: \\[\\mathcal{A}=x^2-9\\]	F	18	TSTA 	auskl
Klammern Sie das folgende aus: \\[\\mathcal{A}=x^2-10x+25\\]	F	19	TSTA 	auskl
Klammern Sie das folgende aus: \\[\\mathcal{A}=8x^3+16x^2-24x\\]	F	20	TSTA 	auskl
Klammern Sie das folgende aus: \\[\\mathcal{A}=4xy+4xz+12y^2+12yz\\]	F	21	TSTA 	auskl
Klammern Sie das folgende aus: \\[\\mathcal{A}=x^2-9\\]	F	22	TSTA 	auskl
Klammern Sie das folgende aus: \\[\\mathcal{A}=4x^3+8x^2-12x\\]	F	24	TSTA 	auskl
Klammern Sie das folgende aus: \\[\\mathcal{A}=3xy+3xz+4y^2+4yz\\]	F	25	TSTA 	auskl
Bestimmen Sie den Quotienten \\(Q(x)\\) bei der Polynomdivision: \\[P=S\\cdot Q+R\\] wobei \\[P(x)=2x^4+18x^3+64x^2+159x+88\\text{~~und~~} S(x)=x^2+3x+11\\]	F	155	TSTA 	pldiv
Bestimmen Sie den Quotienten \\(Q(x)\\) bei der Polynomdivision: \\[P=S\\cdot Q+R\\] wobei \\[P(x)=2x^4+7x^3+40x^2+68x+160\\text{~~und~~} S(x)=x^2+2x+9\\]	F	151	TSTA 	pldiv
Bestimmen Sie den Quotienten \\(Q(x)\\) bei der Polynomdivision: \\[P=S\\cdot Q+R\\] wobei \\[P(x)=4x^4+x^3+30x^2+11x+79\\text{~~und~~} S(x)=x^2+x+3\\]	F	153	TSTA 	pldiv
Bestimmen Sie den Quotienten \\(Q(x)\\) bei der Polynomdivision: \\[P=S\\cdot Q+R\\] wobei \\[P(x)=3x^4+21x^3+63x^2+90x+43\\text{~~und~~} S(x)=x^2+4x+7\\]	F	154	TSTA 	pldiv
Bestimmen Sie den Quotienten \\(Q(x)\\) bei der Polynomdivision: \\[P=S\\cdot Q+R\\] wobei \\[P(x)=x^4+8x^3+28x^2+57x+68\\text{~~und~~} S(x)=x^2+2x+5\\]	F	152	TSTA 	pldiv
Bestimmen Sie den Quotienten \\(Q(x)\\) bei der Polynomdivision: \\[P=S\\cdot Q+R\\] wobei \\[P(x)=2x^4+5x^3+23x^2+36x+46\\text{~~und~~} S(x)=x^2+x+7\\]	F	156	TSTA 	pldiv
Klammern Sie das folgende aus: \\[\\mathcal{A}=x^2-1\\]	F	26	TSTA 	auskl
Klammern Sie das folgende aus: \\[\\mathcal{A}=x^2-16\\]	F	27	TSTA 	auskl
Klammern Sie das folgende aus: \\[\\mathcal{A}=25x^2-120xy+144y^2\\]	F	28	TSTA 	auskl
Klammern Sie das folgende aus: \\[\\mathcal{A}=x^2-4\\]	F	29	TSTA 	auskl
Vereinfachen Sie den Bruch: \\[\\mathcal{W}=\\frac{4 x+4}{1-\\frac{6}{x-4}}\\]	F	67	TSTA 	dopbr
Vereinfachen Sie den Bruch: \\[\\mathcal{W}=\\frac{3}{1+\\frac{x}{x+10}}\\]	F	68	TSTA 	dopbr
Vereinfachen Sie den Bruch: \\[\\mathcal{W}=\\frac{x^2-2}{2+\\frac{14}{x+1}}\\]	F	69	TSTA 	dopbr
Vereinfachen Sie den Bruch: \\[\\mathcal{W}=\\frac{4 x+4}{1-\\frac{14}{x-4}}\\]	F	70	TSTA 	dopbr
Vereinfachen Sie den Bruch: \\[\\mathcal{W}=\\frac{x+4}{1+\\frac{4}{x}}\\]	F	71	TSTA 	dopbr
Vereinfachen Sie den Bruch: \\[\\mathcal{W}=\\frac{1 x+10}{1-\\frac{12}{x-10}}\\]	F	72	TSTA 	dopbr
Vereinfachen Sie den Bruch: \\[\\mathcal{W}=\\frac{x^2-1}{2+\\frac{6}{x+1}}\\]	F	73	TSTA 	dopbr
Vereinfachen Sie den Bruch: \\[\\mathcal{W}=\\frac{x^2-5}{2+\\frac{10}{x+1}}\\]	F	74	TSTA 	dopbr
Vereinfachen Sie den Bruch: \\[\\mathcal{W}=\\frac{2 x+10}{1-\\frac{12}{x-10}}\\]	F	75	TSTA 	dopbr
Zeigen Sie die Stammfunktion \\(y=F(x)\\) von \\[f(x)=\\frac1x\\] mit \\(F(1)=-2\\)	F	91	TSTA 	stamf
Zeigen Sie die Stammfunktion \\(y=F(x)\\) von \\[f(x)=6 x^5\\] mit \\(F(0)=3\\)	F	92	TSTA 	stamf
Zeigen Sie die Stammfunktion \\(y=F(x)\\) von \\[f(x)=6\\cdot e^{6x}\\] mit \\(F(0)=0\\)	F	94	TSTA 	stamf
Zeigen Sie die Stammfunktion \\(y=F(x)\\) von \\[f(x)=\\frac{2x}{x^2+7}\\] mit \\(F(0)=1\\)	F	96	TSTA 	stamf
Bestimmen Sie bitte das unbestimmte Integral: \\[{I}=\\int x\\cdot \\sqrt{x^2+11}\\,dx\\]	F	109	TSTA 	unint
Bestimmen Sie bitte das unbestimmte Integral: \\[{I}=\\int \\frac{2x}{x^2+1}\\,dx\\]	F	111	TSTA 	unint
Bestimmen Sie bitte das unbestimmte Integral: \\[{I}=\\int \\sin(2 x)\\,dx\\]	F	112	TSTA 	unint
Bestimmen Sie bitte das unbestimmte Integral: \\[{I}=\\int \\sin(8 x)\\,dx\\]	F	113	TSTA 	unint
Bestimmen Sie bitte das unbestimmte Integral: \\[I=\\int \\frac{2x}{x^2+7}\\,dx\\]	F	106	TSTA 	unint
Bestimmen Sie bitte das unbestimmte Integral: \\[{I}=\\int x\\cdot \\sqrt{x^2+1}\\,dx\\]	F	107	TSTA 	unint
Berechen Sie die Ableitung der Funktion \\[f(x)=\\ln(x^2+7)+\\cos(x)\\]	F	9	TSTA 	abltn
Zeigen Sie die Stammfunktion \\(y=F(x)\\) von \\[f(x)=2 x\\] mit \\(F(0)=1\\)	F	95	TSTA 	stamf
Berechen Sie die Ableitung der Funktion \\[f(x)=e^{x^2-9x}\\]	F	11	TSTA 	abltn
Berechen Sie die Ableitung der Funktion \\[f(x)=e^{x^2-5x}\\]	F	12	TSTA 	abltn
Berechen Sie die Ableitung der Funktion \\[f(x)=x^2\\cdot \\ln x\\]	F	13	TSTA 	abltn
Berechen Sie die Ableitung der Funktion \\[f(x)=e^{x^2-13x}\\]	F	14	TSTA 	abltn
Berechen Sie die Ableitung der Funktion \\[f(x)=\\cos(e^{x})\\]	F	15	TSTA 	abltn
Berechen Sien Sie die Ableitung der Funktion \\[f(x)=\\frac{x^2+2}{x-5}\\]	F	1	TSTA 	abltn
Berechen Sie die Ableitung der Funktion \\[f(x)=\\ln(x^2+6)+\\cos(2 x)\\]	F	6	TSTA 	abltn
Vereinfachen Sien Sie den Ausdruck: \\[\\mathcal{W}=\\frac{4}{x}+\\frac{10}{x+4}\\]	F	60	TSTA 	brtrm
Bestimmen Sie bitte das unbestimmte Integral: \\[{I}=\\int \\cos(6 x-13)\\,dx\\]	F	115	TSTA 	unint
Bestimmen Sie bitte das unbestimmte Integral: \\[{I}=\\int \\frac1x\\,dx\\]	F	116	TSTA 	unint
Bestimmen Sie bitte das unbestimmte Integral: \\[{I}=\\int x\\cdot \\sqrt{x^2+3}\\,dx\\]	F	117	TSTA 	unint
Klammern Sie das folgende aus: \\[\\mathcal{A}=10x^3+20x^2-30x\\]	F	30	TSTA 	auskl
Multiplizieren Sie das \\[\\mathcal{A}=(x+4)^3\\] bitte aus und geben Sie das Endergebnis an.	F	31	TSTA 	ausml
Multiplizieren Sie das \\[\\mathcal{A}=(x+4 y)\\cdot (x-4 y)\\] bitte aus und geben Sie das Endergebnis an.	F	32	TSTA 	ausml
Multiplizieren Sie das \\[\\mathcal{A}=(x+3 y)\\cdot (x-4 y)\\] bitte aus und geben Sie das Endergebnis an.	F	33	TSTA 	ausml
Multiplizieren Sie das \\[\\mathcal{A}=(x+4)\\cdot (x+10)\\] bitte aus und geben Sie das Endergebnis an.	F	34	TSTA 	ausml
Multiplizieren Sie das \\[\\mathcal{A}=(x+4)^3\\] bitte aus und geben Sie das Endergebnis an.	F	35	TSTA 	ausml
Multiplizieren Sie das \\[\\mathcal{A}=(x-5)\\cdot (x+10)\\] bitte aus und geben Sie das Endergebnis an.	F	36	TSTA 	ausml
Multiplizieren Sie das \\[\\mathcal{A}=(x+1)\\cdot (x+8)\\] bitte aus und geben Sie das Endergebnis an.	F	37	TSTA 	ausml
Multiplizieren Sie das \\[\\mathcal{A}=(3 x+6)^2\\] bitte aus und geben Sie das Endergebnis an.	F	38	TSTA 	ausml
Multiplizieren Sie das \\[\\mathcal{A}=(3 x+2)^2\\] bitte aus und geben Sie das Endergebnis an.	F	39	TSTA 	ausml
Multiplizieren Sie das \\[\\mathcal{A}=(3 x+6)^2\\] bitte aus und geben Sie das Endergebnis an.	F	40	TSTA 	ausml
Multiplizieren Sie das \\[\\mathcal{A}=(x+5)^3\\] bitte aus und geben Sie das Endergebnis an.	F	41	TSTA 	ausml
Multiplizieren Sie das \\[\\mathcal{A}=(x+5)^3\\] bitte aus und geben Sie das Endergebnis an.	F	42	TSTA 	ausml
Multiplizieren Sie das \\[\\mathcal{A}=(x+4)^3\\] bitte aus und geben Sie das Endergebnis an.	F	43	TSTA 	ausml
Multiplizieren Sie das \\[\\mathcal{A}=(x^2-2)\\cdot (x^2+2)\\] bitte aus und geben Sie das Endergebnis an.	F	44	TSTA 	ausml
Multiplizieren Sie das \\[\\mathcal{A}=(x-2)\\cdot (x+4)\\] bitte aus und geben Sie das Endergebnis an.	F	45	TSTA 	ausml
Vereinfachen Sie den Bruch: \\[\\mathcal{W}=\\frac{5}{1+\\frac{x}{x+6}}\\]	F	61	TSTA 	dopbr
Vereinfachen Sie den Bruch: \\[\\mathcal{W}=\\frac{3}{1+\\frac{x}{x+4}}\\]	F	62	TSTA 	dopbr
Vereinfachen Sie den Bruch: \\[\\mathcal{W}=\\frac{x^2-1}{2+\\frac{10}{x+1}}\\]	F	63	TSTA 	dopbr
Vereinfachen Sie den Bruch: \\[\\mathcal{W}=\\frac{4 x+10}{1-\\frac{10}{x-10}}\\]	F	64	TSTA 	dopbr
Vereinfachen Sie den Bruch: \\[\\mathcal{W}=\\frac{x^2-3}{2+\\frac{10}{x+1}}\\]	F	65	TSTA 	dopbr
Vereinfachen Sie den Bruch: \\[\\mathcal{W}=\\frac{3 x+13}{1-\\frac{10}{x-13}}\\]	F	66	TSTA 	dopbr
Vereinfachen Sien Sie den Ausdruck: \\[\\mathcal{W}=\\frac{5}{x}+\\frac{6}{x+5}\\]	F	46	TSTA 	brtrm
Vereinfachen Sien Sie den Ausdruck: \\[\\mathcal{W}=\\frac{x}{x-1}-\\frac{1}{x+1}\\]	F	47	TSTA 	brtrm
Vereinfachen Sien Sie den Ausdruck: \\[\\mathcal{W}=\\frac{x}{x-2}-\\frac{1}{x+2}\\]	F	48	TSTA 	brtrm
Klammern Sie das folgende aus: \\[\\mathcal{A}=x^2-4xy+4y^2\\]	F	23	TSTA 	auskl
Berechen Sie die Ableitung der Funktion \\[f(x)=\\cos(e^{4x})\\]	F	2	TSTA 	abltn
Berechen Sie die Ableitung der Funktion \\[f(x)=e^{x^2-7x}\\]	F	3	TSTA 	abltn
Bestimmen Sie den Quotienten \\(Q(x)\\) bei der Polynomdivision: \\[P=S\\cdot Q+R\\] wobei \\[P(x)=2x^4+8x^3+33x^2+38x+76\\text{~~und~~} S(x)=x^2+x+3\\]	F	157	TSTA 	pldiv
Bestimmen Sie den Quotienten \\(Q(x)\\) bei der Polynomdivision: \\[P=S\\cdot Q+R\\] wobei \\[P(x)=2x^4+6x^3+30x^2+53x+122\\text{~~und~~} S(x)=x^2+3x+7\\]	F	158	TSTA 	pldiv
Bestimmen Sie den Rest \\(R(x)\\) bei der Polynomdivision: \\[P=S\\cdot Q+R\\] wobei \\[P(x)=2x^4+4x^3+48x^2+51x+299\\text{~~und~~} S(x)=x^2+2x+11\\]	F	159	TSTA 	pldiv
Bestimmen Sie den Rest \\(R(x)\\) bei der Polynomdivision: \\[P=S\\cdot Q+R\\] wobei \\[P(x)=3x^4+12x^3+39x^2+47x+73\\text{~~und~~} S(x)=x^2+x+3\\]	F	160	TSTA 	pldiv
Bestimmen Sie den Rest \\(R(x)\\) bei der Polynomdivision: \\[P=S\\cdot Q+R\\] wobei \\[P(x)=3x^4+6x^3+57x^2+63x+247\\text{~~und~~} S(x)=x^2+x+11\\]	F	161	TSTA 	pldiv
Bestimmen Sie den Rest \\(R(x)\\) bei der Polynomdivision: \\[P=S\\cdot Q+R\\] wobei \\[P(x)=3x^4+24x^3+94x^2+214x+186\\text{~~und~~} S(x)=x^2+3x+11\\]	F	162	TSTA 	pldiv
Bestimmen Sie den Rest \\(R(x)\\) bei der Polynomdivision: \\[P=S\\cdot Q+R\\] wobei \\[P(x)=4x^4+23x^3+56x^2+92x+37\\text{~~und~~} S(x)=x^2+2x+5\\]	F	163	TSTA 	pldiv
Bestimmen Sie den Rest \\(R(x)\\) bei der Polynomdivision: \\[P=S\\cdot Q+R\\] wobei \\[P(x)=2x^4+6x^3+3x^2+10x+20\\text{~~und~~} S(x)=x^2+3x+1\\]	F	164	TSTA 	pldiv
Bestimmen Sie den Rest \\(R(x)\\) bei der Polynomdivision: \\[P=S\\cdot Q+R\\] wobei \\[P(x)=4x^4+16x^3+49x^2+91x+157\\text{~~und~~} S(x)=x^2+4x+7\\]	F	165	TSTA 	pldiv
Berechen Sie die Ableitung der Funktion \\[f(x)=\\sqrt{x^2+3}\\]	F	4	TSTA 	abltn
Berechen Sie die Ableitung der Funktion \\[f(x)=\\frac{x^2+5}{x-3}\\]	F	5	TSTA 	abltn
Berechen Sie die Ableitung der Funktion \\[f(x)=\\sin(5x^2)+\\ln x\\]	F	7	TSTA 	abltn
Berechen Sie die Ableitung der Funktion \\[f(x)=e^{6x}\\cdot \\sin(x)\\]	F	8	TSTA 	abltn
Berechen Sie die Ableitung der Funktion \\[f(x)=e^{x^2-7x}\\]	F	10	TSTA 	abltn
Vereinfachen Sien Sie den Ausdruck: \\[\\mathcal{W}=\\frac{6}{x}+\\frac{4}{x+6}\\]	F	49	TSTA 	brtrm
Vereinfachen Sien Sie den Ausdruck: \\[\\mathcal{W}=\\frac{5}{x}+\\frac{8}{x+5}\\]	F	50	TSTA 	brtrm
Vereinfachen Sien Sie den Ausdruck: \\[\\mathcal{W}=\\frac{1}{x-4}+\\frac{1}{x+4}\\]	F	51	TSTA 	brtrm
Vereinfachen Sien Sie den Ausdruck: \\[\\mathcal{W}=\\frac{5}{x}+\\frac{10}{x+5}\\]	F	54	TSTA 	brtrm
Vereinfachen Sien Sie den Ausdruck: \\[\\mathcal{W}=\\frac{x}{x+1}+\\frac{x}{x-1}\\]	F	56	TSTA 	brtrm
Vereinfachen Sien Sie den Ausdruck: \\[\\mathcal{W}=\\frac{1}{x-3}+\\frac{1}{x+3}\\]	F	57	TSTA 	brtrm
Vereinfachen Sien Sie den Ausdruck: \\[\\mathcal{W}=\\frac{1}{x-4}+\\frac{1}{x+4}\\]	F	58	TSTA 	brtrm
Vereinfachen Sien Sie den Ausdruck: \\[\\mathcal{W}=\\frac{4}{x}+\\frac{8}{x+4}\\]	F	59	TSTA 	brtrm
Zeigen Sie die Stammfunktion \\(y=F(x)\\) von \\[f(x)=\\frac1x\\] mit \\(F(1)=-2\\)	F	97	TSTA 	stamf
Zeigen Sie die Stammfunktion \\(y=F(x)\\) von \\[f(x)=\\frac1x\\] mit \\(F(1)=2\\)	F	98	TSTA 	stamf
Zeigen Sie die Stammfunktion \\(y=F(x)\\) von \\[f(x)=7\\cdot \\cos(7 x)\\] mit \\(F(0)=-3\\)	F	99	TSTA 	stamf
Zeigen Sie die Stammfunktion \\(y=F(x)\\) von \\[f(x)=7\\cdot e^{7x}\\] mit \\(F(0)=-1\\)	F	100	TSTA 	stamf
Zeigen Sie die Stammfunktion \\(y=F(x)\\) von \\[f(x)=3 x^2\\] mit \\(F(0)=2\\)	F	101	TSTA 	stamf
Zeigen Sie die Stammfunktion \\(y=F(x)\\) von \\[f(x)=3 x^2\\] mit \\(F(0)=1\\)	F	102	TSTA 	stamf
Zeigen Sie die Stammfunktion \\(y=F(x)\\) von \\[f(x)=3\\cdot \\cos(3 x)\\] mit \\(F(0)=-2\\)	F	103	TSTA 	stamf
Zeigen Sie die Stammfunktion \\(y=F(x)\\) von \\[f(x)=6\\cdot \\cos(6 x)\\] mit \\(F(0)=1\\)	F	104	TSTA 	stamf
Zeigen Sie die Stammfunktion \\(y=F(x)\\) von \\[f(x)=\\frac{2x}{x^2+4}\\] mit \\(F(0)=0\\)	F	105	TSTA 	stamf
Zeigen Sie die Stammfunktion \\(y=F(x)\\) von \\[f(x)=2 x\\] mit \\(F(0)=0\\)	F	93	TSTA 	stamf
Bestimmen Sie bitte das unbestimmte Integral: \\[{I}=\\int 8\\cdot e^{8x}\\,dx\\]	F	110	TSTA 	unint
Bestimmen Sie bitte das unbestimmte Integral: \\[{I}=\\int \\cos(5 x-9)\\,dx\\]	F	118	TSTA 	unint
Bestimmen Sie bitte das unbestimmte Integral: \\[{I}=\\int x\\cdot \\sqrt{x^2+13}\\,dx\\]	F	119	TSTA 	unint
Bestimmen Sie bitte das unbestimmte Integral: \\[{I}=\\int 7\\cdot e^{7x}\\,dx\\]	F	120	TSTA 	unint
Bestimmen Sie bitte das unbestimmte Integral: \\[{I}=\\int(7x^6-\\cos(x))\\,dx\\]	F	108	TSTA 	unint
Bestimmen Sie bitte das unbestimmte Integral: \\[{I}=\\int(2x-\\cos(x))\\,dx\\]	F	114	TSTA 	unint
\.


--
-- Data for Name: kapitel; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.kapitel (kapitel, "kap_kürzel") FROM stdin;
Aufgabenauswahl	TSTA
\.


--
-- Data for Name: themen; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.themen (thema, "th_kürzel", kapitel, blocked) FROM stdin;
Ableitungen	abltn	TSTA	N
Stammfunktionen	stamf	TSTA	N
Unbestimmte Integrale	unint	TSTA	N
Doppelbrüche	dopbr	TSTA	N
Polynomdivision	pldiv	TSTA	N
Ausmultiziplieren	ausml	TSTA	N
Ausklammern	auskl	TSTA	N
Bruchterme	brtrm	TSTA	N
\.


--
-- PostgreSQL database dump complete
--

\unrestrict Ry6QC1EByOdEW4EQPiA2rbQ3lQFoP2EYYCfdTD1AViOmTvidgEBAXIdZ72J3hlS

