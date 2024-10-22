<?xml version="1.0" encoding="UTF-8"?>

<!-- ********************************************************************************************************************************
   ***  sort transcription performance data.xsl
   ***
   ***  Sort a file of transcription performance data by user-specified primary and secondary key
   *** ___________________________________________________________________________________________
   ***
   ***  Last Updated: 27 June 2024
   ***  Version: 1.0
   ***
   ***  Author(s):
   ***     version 1.0:  code by Phil Pfeiffer, Spring 2024
   *** ___________________________________________________________________________________
   ***
   ***  Inputs:
   ***     an XML document of the form
   ***       <...>
   ***          ...
   ***          <performance_data>
   ***             <status>...</status>
   ***             <outcome>....</outcome>
   ***             <transcription_time>       <minutes>...</minutes> <seconds>...</seconds>  </transcription_time>
   ***             <diarization_time>         <minutes>...</minutes> <seconds>...</seconds>  </diarization_time>
   ***             <speaker_assignment_time>  <minutes>...</minutes> <seconds>...</seconds>  </speaker_assignment_time>
   ***             <total_time>               <minutes>...</minutes> <seconds>...</seconds>  </total_time>
   ***             <total_segment_count>...</total_segment_count>
   ***             <bad_segment_count>...</bad_segment_count>
   ***             <bad_segment_list>...</bad_segment_list>
   ***             <recording>...</recording>
   ***             <recording_size>...</recording_size>
   ***             <transcription>(prefix...)\{year}_{language_model}\{weekday}\{venue}\(...suffix)</transcription>
   ***          </performance_data>
   ***          ...
   ***     up to four command line parameters:
   ***         primary_key:          primary sort key         
   ***            supported values:  status, outcome, 
   ***                               transcription_time, diarization_time, speaker_assignment_time, total_time,
   ***                               total_segment_count, bad_segment_count, recording, recording_size, 
   ***                               year, language_model, venue, bad_segment_percentage
   ***            default:           recording_size 
   ***         primary_direction:    ascending or descending  (default: descending)  
   ***         secondary_key:        secondary sort key
   ***            supported values:  same as primary_key 
   ***         secondary_direction:  ascending or descending  (default: descending)  
   ***   -.  standard output:  
   ***       an XML document of performance_data, sorted according to the keys, with additional fields for 
   ***          transcription_time_seconds, diarization_time_seconds, speaker_assignment_time_seconds, total_time_seconds,
   ***          year, language_model, venue, and bad_segment_percentage
   ***
   ***  Status:
   ***  *.  In progress
   ***  ___________________________________
   ***
   ***  Usage Notes:
   ***    -.  (sample) Saxon execution command:
   ***        Transform.exe -xsl:"sort transcription performance data.xsl" -s:...source file....  -o:...output file... \
   ***           primary_key=total_segment_count primary_direction=ascending
   *********************************************************************************************************************************
-->

<xsl:stylesheet 
   version="2.0"
   xmlns:xs="http://www.w3.org/2001/XMLSchema"
   xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
   xmlns:local="http://www.etsu.edu/gradapp-project/"
   extension-element-prefixes="local"
>
   <xsl:param  name="primary_key"         select="'recording_size'" /> 
   <xsl:param  name="primary_direction"   select="'descending'" /> 
   <xsl:param  name="secondary_key" /> 
   <xsl:param  name="secondary_direction" select="'descending'"/> 
   
   <xsl:output   encoding="UTF-8"   omit-xml-declaration="yes" /> 
   
   <xsl:template match="document-node()">
      <!-- make a prepass over the data, if needed, to generate "summary time" elements -->
      <xsl:variable name="augmented_summary_data">
         <xsl:for-each select="//performance_data">
            <xsl:element name="performance_data">
               <!-- convert times to seconds to support duration-based comparisons -->
               <xsl:variable name="transcription_time_seconds"       select="local:toSeconds(transcription_time)"/>
               <xsl:variable name="diarization_time_seconds"         select="local:toSeconds(diarization_time)"/>
               <xsl:variable name="speaker_assignment_time_seconds"  select="local:toSeconds(speaker_assignment_time)"/>
               <xsl:variable name="total_time_seconds"               select="local:toSeconds(total_time)"/>
               <!-- create temporary elements to head this recording's transcription performance data, for ease of sorting -->
               <xsl:element  name="transcription_time">      <xsl:value-of select="$transcription_time_seconds"/>      </xsl:element>
               <xsl:element  name="diarization_time">        <xsl:value-of select="$diarization_time_seconds"/>        </xsl:element>
               <xsl:element  name="speaker_assignment_time"> <xsl:value-of select="$speaker_assignment_time_seconds"/> </xsl:element>
               <xsl:element  name="total_time">              <xsl:value-of select="$total_time_seconds"/>              </xsl:element>
               <!-- take what's there for this transcripption's performance data -->
               <xsl:copy-of select="*"/>
               <!-- add fields to support additional analyses -->
               <xsl:element  name="transcription_time_seconds">      <xsl:value-of select="$transcription_time_seconds"/>      </xsl:element>
               <xsl:element  name="diarization_time_seconds">        <xsl:value-of select="$diarization_time_seconds"/>        </xsl:element>
               <xsl:element  name="speaker_assignment_time_seconds"> <xsl:value-of select="$speaker_assignment_time_seconds"/> </xsl:element>
               <xsl:element  name="total_time_seconds">              <xsl:value-of select="$total_time_seconds"/>              </xsl:element>
               <xsl:analyze-string select="transcription" regex="^.+\\(20\d\d)_((large)|(medium)|(small))\\[^\\]+\\([^\\]+)">
                  <xsl:matching-substring>
                     <xsl:element name="year">           <xsl:value-of select="regex-group(1)"/> </xsl:element>
                     <xsl:element name="language_model"> <xsl:value-of select="regex-group(2)"/> </xsl:element>
                     <xsl:element name="venue">          <xsl:value-of select="regex-group(6)"/> </xsl:element>
                  </xsl:matching-substring>
               </xsl:analyze-string>
               <!-- Saxon HE doesn't support format-number(), so we'll generate percentages by hand -->
               <xsl:variable name="b_s_count" select="bad_segment_count/text()"   as="xs:integer"/>
               <xsl:variable name="t_s_count" select="total_segment_count/text()" as="xs:integer"/>
               <xsl:element name="bad_segment_percentage">  
                  <xsl:choose>
                     <xsl:when test="$t_s_count eq 0"> <xsl:value-of select="0"/> </xsl:when>
                     <xsl:otherwise> <xsl:value-of select="round(10000*$b_s_count div $t_s_count) div 100"/> </xsl:otherwise>
                  </xsl:choose>
               </xsl:element>
            </xsl:element>
         </xsl:for-each>
      </xsl:variable>
      <!-- do the sort, outputting the sorted data -->
      <xsl:element name="summary_data">
         <xsl:for-each select="$augmented_summary_data//performance_data">
            <xsl:sort select="*[name()=$primary_key][1]"    data-type="{local:keyType($primary_key)}"    order="{$primary_direction}"/>
            <xsl:sort select="*[name()=$secondary_key][1]"  data-type="{local:keyType($secondary_key)}"  order="{$secondary_direction}"/>
            <xsl:element name="performance_data">
               <!-- "gt 4" dumps the four special elements introduced for duration-based comparisons -->
               <xsl:copy-of select="*[position() gt 4]"/>
            </xsl:element>
         </xsl:for-each>
      </xsl:element>
   </xsl:template>

   <!-- convert time_element/{minutes,seconds} to seconds -->
   <xsl:function name="local:toSeconds">
      <xsl:param name="time_element"/>
      <xsl:value-of select="60*$time_element/minutes/text() + $time_element/seconds/text()"/>
   </xsl:function>

   <xsl:variable 
       name="numeric_element_types" 
       select="('transcription_time', 'diarization_time', 'speaker_assignment_time', 'total_time', 'total_segment_count', 'bad_segment_count', 'recording_size', 'bad_segment_percentage')"
   />
   
   <!-- return key type for element -->
   <xsl:function name="local:keyType">
      <xsl:param name="key_name"/>
      <xsl:choose>
         <xsl:when test="$key_name = $numeric_element_types"> <xsl:value-of select="'number'"/>  </xsl:when>
         <xsl:otherwise>  <xsl:value-of select="'text'"/>  </xsl:otherwise>
      </xsl:choose>
   </xsl:function>

</xsl:stylesheet>
