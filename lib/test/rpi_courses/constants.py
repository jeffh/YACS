import os

ROOT = os.path.abspath(os.path.dirname(__file__))
ROOT_TEST_DATA = os.path.join(ROOT, 'test_data')

XML_FILE = os.path.join(ROOT_TEST_DATA, 'rpi_courses.xml')
XML_PARSER_FILE = os.path.join(ROOT_TEST_DATA, 'rpi_shorthand.xml')
XML_SCHEDULE_TEST_FILE = os.path.join(ROOT_TEST_DATA, 'rpi_schedule_test.xml')
XML_SCHEDULE_TEST_CONFLICT_FILE = os.path.join(ROOT_TEST_DATA, 'rpi_schedule_conflict_test.xml')
SIS_FILE_SPRING2012 = os.path.join(ROOT_TEST_DATA, 'sis_courses_spring2012.htm')

HTML = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<HTML>
 <HEAD>
  <TITLE>Index of /reg/rocs</TITLE>
 </HEAD>
 <BODY>
<H1>Index of /reg/rocs</H1>
<PRE><IMG SRC="/icons/blank.gif" ALT="     "> <A HREF="?N=D">Name</A>                    <A HREF="?M=A">Last modified</A>       <A HREF="?S=A">Size</A>  <A HREF="?D=A">Description</A>
<HR>
<IMG SRC="/icons/back.gif" ALT="[DIR]"> <A HREF="/reg/">Parent Directory</A>        18-Oct-2010 20:37      -
<IMG SRC="/icons/unknown.gif" ALT="[   ]"> <A HREF="201001.xml">201001.xml</A>              28-Sep-2010 10:23   719k
<IMG SRC="/icons/unknown.gif" ALT="[   ]"> <A HREF="201005.xml">201005.xml</A>              28-Sep-2010 10:23    42k
<IMG SRC="/icons/unknown.gif" ALT="[   ]"> <A HREF="201009.xml">201009.xml</A>              03-Nov-2010 21:00   730k
<IMG SRC="/icons/text.gif" ALT="[TXT]"> <A HREF="201009.xml_old">201009.xml_old</A>          28-Sep-2010 10:23   698k
<IMG SRC="/icons/unknown.gif" ALT="[   ]"> <A HREF="201101.xml">201101.xml</A>              17-Nov-2010 14:16   713k
<IMG SRC="/icons/text.gif" ALT="[TXT]"> <A HREF="testrocs.txt">testrocs.txt</A>            28-Sep-2010 10:23     1k
</PRE><HR>
<ADDRESS>Oracle-Application-Server-10g/10.1.2.2.0 Oracle-HTTP-Server Server at sis.rpi.edu Port 80</ADDRESS>
</BODY></HTML>"""
