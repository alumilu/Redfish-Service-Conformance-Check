# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/LICENSE.md

# File: rfs_check.py
# Description: Redfish service conformance check tool. This module contains implemented assertions for 
#   SUT.These assertions are based on operational checks on Redfish Service to verify that it conforms 
#   to the normative statements from the Redfish specification. 
#   See assertions in redfish-assertions.xlxs for assertions summary

import sys
import re
import rf_utility

# map python 2 vs 3 imports
if (sys.version_info < (3, 0)):
    # Python 2
    Python3 = False
    from urlparse import urlparse
    from StringIO import StringIO
    from httplib import HTTPSConnection, HTTPConnection, HTTPResponse
    import urllib
    import urllib2
else:
    # Python 3
    Python3 = True
    from urllib.parse import urlparse
    from io import StringIO
    from http.client import HTTPSConnection, HTTPConnection, HTTPResponse
    from urllib.request import urlopen


import ssl
import re
import json
import argparse
import base64
import datetime
import types
import socket
import select
import os
from collections import OrderedDict
import time

# current spec followed for these assertions
REDFISH_SPEC_VERSION = "Version 1.0.2"

#todo: check 7.x via json schemas aswell where applicable..
###################################################################################################
# Name: Assertion_7_0_1(self, log) :Data Model                                             
# Assertion text: 
#   1. Each resource shall be strongly typed according to a resource type definition (basically in
#   EntityType elements with Name and Basetype if any, thats what we are looking for)
#      (should we verify the format?: namespace.v(ersion if any).typename
#   2. The type shall be defined in a Redfish schema document (verify against the namespace identified)  
#   should we check for all relative uris?           
###################################################################################################
def Assertion_7_0_1(self, log):
    log.AssertionID = '7.0.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris # contains all the urls found in every navigation property of all schemas

    for rf_schema in csdl_schema_model.RedfishSchemas:
        #start from resource
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            for entity_type in r_namespace.EntityTypes:
                if entity_type.BaseType:
                    # call function to verify if basetype is strongly typed that is the type is defined in the schemas 
                    namespace_found, typename_found = csdl_schema_model.verify_resource_basetype(entity_type.BaseType)
                    if not typename_found:
                        assertion_status = log.FAIL
                        log.assertion_log('line', "Resource %s, Basetype %s is not strongly typed as expected" % (entity_type.Name, entity_type.BaseType))  # instead of this just add it in the dictionary of errors to be printed later              

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion_7_0_1

###################################################################################################
# Name: Assertion_7_1_1(self, log)  Type Identifiers in JSON                                
# Assertion text: 
#  Types used within a JSON payload shall be defined in, or referenced, by the metadata document. 
#  metadata document is the document retreived from $metadata 
#  Method: 1. DEFINED IN: Parse @odata.type according to format Namespace.Typename.. Verify 
#             Namespace against Include element in #metadata, then within the Schema File referenced 
#             for the Namespace matched in $metadata, we verify the Typename. 
#     TODO 2. REFERENCED BY: If a Namespace is not found in $metadata, we go through each Url 
#             referenced in the $metadata and try to find it within the References element of each
#             schema file.
###################################################################################################
def Assertion_7_1_1(self, log):
    log.AssertionID = '7.1.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris # contains all the urls found in every navigation property of all schemas
    
    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = rf_utility.parse_odata_type(json_payload['@odata.type'])
                if namespace and typename:
                    if self.metadata_document_structure:
                        # we already have a metadata document mapped out in metadata_document_structure for this service in rf_utility
                        type_found = csdl_schema_model.verify_resource_metadata_reference(namespace, typename, self.metadata_document_structure)
                        if not type_found:
                            assertion_status = log.FAIL
                            log.assertion_log('line', "Type used within json payload for resource: %s, '@odata.type': %s is not defined in or referenced by the service's $metadata document: %s as expected" % (relative_uris[relative_uri], json_payload['@odata.type'], self.Redfish_URIs['Service_Metadata_Doc']))  
                    else:
                        assertion_status = log.WARN
                        log.assertion_log('line', 'Service $metadata document %s not found' % (self.Redfish_URIs['Service_Metadata_Doc']))

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 7.1.1

###################################################################################################
# Name: Assertion_7_2_1(self, log)                                                
# Assertion text: 
#   Resource Name, Property Names and constants such as Enumerations shall be Pascal-cased
#   The first letter of each work shall be upper case with spaces between words shall be removed                
###################################################################################################
def WIP_Assertion_7_2_1(self, log):
 
    log.AssertionID = '7.2.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    log.assertion_log(assertion_status, None)

    return (assertion_status)
#
## end Assertion 7_2_1

###################################################################################################
# Name: Assertion_7_4_3(self, log)  Schema Documents                                                
# Assertion text: 
#   The outer element of the OData Schema representation document shall be the Edmx element, and shall 
#   have a 'Version' attribute with a value of "4.0".    
###################################################################################################
def Assertion_7_4_3(self, log):
    log.AssertionID = '7.4.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    csdl_schema_model = self.csdl_schema_model

    for schema in csdl_schema_model.FullRedfishSchemas:
        if csdl_schema_model.map_element_to_csdlnamespace('Edmx') != schema.edmx:
            assertion_status = log.FAIL
            log.assertion_log('line', "~ The outer element of the OData Schema representation document %s is not the Edmx element, instead found %s" % (rf_schema.SchemaUri, schema.edmx))
        if schema.Version is None:
            assertion_status = log.FAIL
            log.assertion_log('line', "~ The outer Edmx element of the OData Schema representation document %s does not have a 'Version' attribute" % rf_schema.SchemaUri)
        elif schema.Version != '4.0':
            assertion_status = log.FAIL
            log.assertion_log('line', "~ The outer Edmx element of the OData Schema representation document %s does not have a value of '4.0' in the 'Version' attribute, instead found %s" % (rf_schema.SchemaUri, schema.Version))

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_4_3

###################################################################################################
# Name: Assertion_7_4_4(self, log)  Resource Type Definitions                                                
# Assertion text: 
# All resources shall include Description and LongDescription annotations i.e EntityTypes under Schema
###################################################################################################
def Assertion_7_4_4(self, log):
    log.AssertionID = '7.4.4'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            entity_types = r_namespace.EntityTypes
            for entity_type in entity_types:
                if not csdl_schema_model.verify_annotation_recur(entity_type,'OData.Description'): #should alias be prepended or should this be independent of Alias?
                   assertion_status = log.FAIL
                   log.assertion_log('line', "~ Resource: %s, BaseType: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.Description' in its OData schema representation document: %s" % (entity_type.Name, entity_type.BaseType, rf_schema.SchemaUri))
                if not csdl_schema_model.verify_annotation_recur(entity_type,'OData.LongDescription'): #should alias be prepended or should this be independent of Alias?
                   assertion_status = log.FAIL
                   log.assertion_log('line', "~ Resource: %s, BaseType: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.LongDescription' in its OData schema representation document: %s" % (entity_type.Name, entity_type.BaseType, rf_schema.SchemaUri))   

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_4_4

###################################################################################################
# Name: Assertion_7_4_6(self, log)  Resource Properties                                                
# Assertion text: 
# All properties shall include Description and LongDescription annotations.  Checking all
# Property types : Property (within EntityType and ComplexType)
###################################################################################################
def Assertion_7_4_6(self, log):
    log.AssertionID = '7.4.6'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    ns_tag = 'Property'
    find_ns_tag = ['Annotation']

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            for entity_type in r_namespace.EntityTypes:
                for prop in entity_type.Properties:
                    if not csdl_schema_model.verify_annotation_recur(prop,'OData.Description'): #should alias be prepended or should this be independent of Alias?
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ Property: %s, Type: %s and any of its parent Type resources (based on inheritance) does not have annotation 'OData.Description' in its OData schema representation document: %s" % (prop.Name, prop.Type, rf_schema.SchemaUri))
                    if not csdl_schema_model.verify_annotation_recur(prop,'OData.LongDescription'): #should alias be prepended or should this be independent of Alias?
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ Property: %s, Type: %s and any of its parent Type resources (based on inheritance) does not have annotation 'OData.LongDescription' in its OData schema representation document: %s" % (prop.Name, prop.Type, rf_schema.SchemaUri))   

            for complextype in r_namespace.ComplexTypes:
                for prop in complextype.Properties:
                    if not csdl_schema_model.verify_annotation_recur(prop,'OData.Description'): #should alias be prepended or should this be independent of Alias?
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ Property: %s, Type: %s and any of its parent Type resources (based on inheritance) does not have annotation 'OData.Description' in its OData schema representation document: %s" % (prop.Name, prop.Type, rf_schema.SchemaUri))
                    if not csdl_schema_model.verify_annotation_recur(prop,'OData.LongDescription'): #should alias be prepended or should this be independent of Alias?
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ Property: %s, Type: %s and any of its parent Type resources (based on inheritance) does not have annotation 'OData.LongDescription' in its OData schema representation document: %s" % (prop.Name, prop.Type, rf_schema.SchemaUri))   

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_4_6

###################################################################################################
# Name: Assertion_7_4_8(self, log)  Resource Properties                                                
# Assertion text: 
# Structured types shall include Description and LongDescription annotations. i.e ComplexTypes 
###################################################################################################
def Assertion_7_4_8(self, log):
    log.AssertionID = '7.4.8'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    
    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            complextypes = r_namespace.ComplexTypes
            for complextype in complextypes:
                if not csdl_schema_model.verify_annotation_recur(complextype,'OData.Description'): #should alias be prepended or should this be independent of Alias?
                   assertion_status = log.FAIL
                   log.assertion_log('line', "~ ComplexType: %s, BaseType: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.Description' in its OData schema representation document: %s" % (complextype.Name, complextype.BaseType, rf_schema.SchemaUri))
                if not csdl_schema_model.verify_annotation_recur(complextype,'OData.LongDescription'): #should alias be prepended or should this be independent of Alias?
                   assertion_status = log.FAIL
                   log.assertion_log('line', "~ ComplexType: %s, BaseType: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.LongDescription' in its OData schema representation document: %s" % (complextype.Name, complextype.BaseType, rf_schema.SchemaUri))   

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_4_8

###################################################################################################
# Name: Assertion_7_4_9(self, log)  Enums                                              
# Assertion text: 
# Enumeration Types shall include Description and LongDescription annotations.
###################################################################################################
def Assertion_7_4_9(self, log):
    log.AssertionID = '7.4.9'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            enum_types = r_namespace.EnumTypes
            for enum_type in enum_types:
                if not csdl_schema_model.verify_annotation(enum_type,'OData.Description'): #should alias be prepended or should this be independent of Alias?
                   assertion_status = log.FAIL
                   log.assertion_log('line', "~ EnumType: %s within Schema Namespace: %s does not have annotation 'OData.Description' in its OData schema representation document: %s" % (enum_type.Name, r_namespace.Namespace, rf_schema.SchemaUri))
                if not csdl_schema_model.verify_annotation(enum_type, 'OData.LongDescription'): #should alias be prepended or should this be independent of Alias?
                   assertion_status = log.FAIL
                   log.assertion_log('line', "~ EnumType: %s within Schema Namespace: %s does not have annotation 'OData.LongDescription' in its OData schema representation document: %s" % (enum_type.Name, r_namespace.Namespace, rf_schema.SchemaUri))   

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_4_9
###################################################################################################
# Name: Assertion_7_4_10(self, log)  Enums                                              
# Assertion text: 
# Enumeration Members shall include Description annotations.
###################################################################################################
def Assertion_7_4_10(self, log):
    log.AssertionID = '7.4.10'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    
    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            enum_types = r_namespace.EnumTypes
            for enum_type in enum_types:
                for member in enum_type.Members:
                    if not csdl_schema_model.verify_annotation(member, 'OData.Description'): #should alias be prepended or should this be independent of Alias?
                       assertion_status = log.FAIL
                       log.assertion_log('line', "~ Member: %s of EnumType: %s does not have annotation 'OData.Description' in its OData schema representation document: %s" % (member.Name, enum_type.Name, rf_schema.SchemaUri))             

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_4_10

###################################################################################################
# Name: check_addprop_annotation()
#   This function checks for additional properties annotation within a resource type
#   and based on 
###################################################################################################
def find_addprop_annotation(self, xtype):
    additional_property = self.csdl_schema_model.get_annotation(xtype, 'OData.AdditionalProperties')
    if additional_property:
        if additional_property.AttrValue:
            if additional_property.AttrValue == 'False':
                return False
    return True

###################################################################################################
# Name: get_resource_additionalprop():
# returns any addtional properties found in payload
###################################################################################################
def get_resource_additionalprop(self, json_payload, xtype, namespace = None):
    # AdditionalProperties is False, we dont need to do the following...
    for key in json_payload:
        # first check if its in the common properties list
        if key in self.csdl_schema_model.CommonRedfishResourceProperties:
            continue
        # need to ignore @odata properties
        elif '@odata' in key:
            continue
        # not an odata property, nor a common property, it should be in this resource's defined properties (if inheritence use recur)
        elif self.csdl_schema_model.verify_property_in_resource_recur(xtype, key, namespace):
            continue                                         
        #this could potentially be the additional property
        return key 

    return None

###################################################################################################
# Name: Assertion_7_4_11(self, log)  Additional Properties  - checked via xml metadata                                     
# Assertion text: 
# The AdditionalProperties annotation term is used to specify whether a type can contain additional 
# properties outside of those defined. Types annotated with the AdditionalProperties annotation with 
# a Boolean attribute with a value of "False", must not contain additional properties.
# applies to EntityTypes and ComplexType Annotations
# Reference: https://tools.oasis-open.org/version-control/browse/wsvn/odata/trunk/spec/vocabularies/Org.OData.Core.V1.xml
# specification unclear. Description for AdditionalProperties states : 
# String="Instances of this type may contain properties in addition to those declared in $metadata", 
# does it mean the context url of the resource?
###################################################################################################
def _Assertion_7_4_11(self, log):
    log.AssertionID = '7.4.11'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = csdl_schema_model.get_resource_namespace_typename(json_payload['@odata.type'])
                if namespace and typename:
                    if not find_addprop_annotation(self, typename):
                        # AdditionalProperties is False, if it were True, we dont need to do the following...
                        property_key = get_resource_additionalprop(self, json_payload, typename, namespace)
                        if property_key: 
                            assertion_status = log.FAIL
                            log.assertion_log('line', "~ Resource: %s has EntityType: %s with Annotation 'AdditionalProperty' set to False in its schema document %s, but additional property: %s found in resource payload" % (json_payload['@odata.id'], typename.Name, namespace.SchemaUri, property_key))  
                                     
                    '''     
                    for complextype in namespace.ComplexTypes:
                        if not find_addprop_annotation(self, complextype):
                            # complextype name and some simple property name could be the same, (example Actions, Links found in serviceroot.xml and computersystem.xml).. make sure its a complextype key in payload.
                            if complextype.Name in json_payload.keys() and isinstance(json_payload[complextype.Name], dict):
                                sub_payload = json_payload[complextype.Name]
                                #find complextype.name and properties within that
                                property_key = get_resource_additionalprop(self, sub_payload, complextype)
                                if property_key:                                         
                                    assertion_status = log.FAIL
                                    log.assertion_log('line', "~ Resource: %s has ComplexType: %s with Annotation 'AdditionalProperty' set to False in its schema document %s, but an additional property: %s found in resource payload" % (json_payload['@odata.id'], complextype.Name, namespace.SchemaUri, property_key))                                      
                                   
                    '''
    log.assertion_log(assertion_status, None)
    return (assertion_status)

###################################################################################################
# verify_typename_in_json_metadata(typename, json_metadata):
# verifies if typename exists in resources json schema document. Search for it under 'definitions'
###################################################################################################
def verify_typename_in_json_metadata(typename, json_metadata):
    if 'definitions' in json_metadata:
        if json_metadata['definitions']:
            if typename in json_metadata['definitions']:
                return True
    return False
           
###################################################################################################
# Name: Assertion_7_4_11(self, log)  Additional Properties   - checked via json metadata                                        
# Assertion text: 
# The AdditionalProperties annotation term is used to specify whether a type can contain additional 
# properties outside of those defined. Types annotated with the AdditionalProperties annotation with 
# a Boolean attribute with a value of "False", must not contain additional properties.
# applies to EntityTypes and ComplexType Annotations
# Reference: https://tools.oasis-open.org/version-control/browse/wsvn/odata/trunk/spec/vocabularies/Org.OData.Core.V1.xml
# specification unclear. Description for AdditionalProperties states : 
# String="Instances of this type may contain properties in addition to those declared in $metadata", 
# does it mean the context url of the resource?
###################################################################################################
def Assertion_7_4_11(self, log):
    log.AssertionID = '7.4.11'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    #camelcased? need to verify this...
    annotation_term = 'additionalProperties'

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = rf_utility.parse_odata_type(json_payload['@odata.type'])
                if namespace and typename:
                    json_metadata, schema_file = rf_utility.get_resource_json_metadata(namespace, self.json_directory)     
                    if json_metadata and schema_file:           
                        if verify_typename_in_json_metadata(typename, json_metadata):
                            if annotation_term in json_metadata['definitions'][typename]:
                                if not json_metadata['definitions'][typename][annotation_term]:
                                    # if value is False then check if there are any additional properties, which it shouldnt
                                    if 'properties' in json_metadata['definitions'][typename]:
                                        for property_key in json_payload:
                                            if property_key not in json_metadata['definitions'][typename]['properties']:
                                                assertion_status = log.FAIL
                                                log.assertion_log('line', "~ Resource: %s of type: %s has Annotation: '%s' set to 'False' in its schema document %s, but additional property: %s found in resource payload" % (json_payload['@odata.id'], namespace, annotation_term, schema_file, property_key))  
    log.assertion_log(assertion_status, None)
    return (assertion_status)

###################################################################################################
# check_required_property_in_payload()
#   This function checks the payload for a required 'Property' key 
###################################################################################################
def check_required_property_in_payload(required_property, property_name, json_payload):
    if not required_property.AttrValue or required_property.AttrValue != 'false':
        #check payload, must have it
        for key in json_payload:
            if key == property_name:
                return True
        return False

###################################################################################################
# Name: Assertion_7_4_13(self, log)  Required Properties    - checked via xml schema                                
# Assertion text: 
# If an implementation supports a property, it shall always provide a value for that property.
# If a value is unknown, then null is an acceptable values in most cases. 
# required is True by default, so unless it is a False, it should be in the payload with a value or null
###################################################################################################
def _Assertion_7_4_13(self, log):
    log.AssertionID = '7.4.13'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = csdl_schema_model.get_resource_namespace_typename(json_payload['@odata.type'])
                if namespace and typename:
                    #structural property
                    for property in typename.Properties:
                        required_property = csdl_schema_model.get_annotation(property, 'Redfish.Required')
                        if required_property:
                            if not check_required_property_in_payload(required_property, property.Name, json_payload):
                                assertion_status = log.FAIL
                                log.assertion_log('line', "Resource %s contains a Property %s which has Annotation 'Redfish.Required' set to 'True' but property not found in its resource payload %s" % (typename.Name, property.Name, json_payload['@odata.id']))
                  
                    #reference property
                    for navproperty in typename.NavigationProperties:
                        required_property = csdl_schema_model.get_annotation(navproperty, 'Redfish.Required')
                        if required_property:
                            if not check_required_property_in_payload(required_property, navproperty.Name, json_payload):
                                assertion_status = log.FAIL
                                log.assertion_log('line', "Resource %s contains a Navigation Property %s which has Annotation 'Redfish.Required' set to 'True' but property not found in its resource payload %s" % (typename.Name, property.Name, json_payload['@odata.id']))
                  
    log.assertion_log(assertion_status, None)
    return (assertion_status)

###################################################################################################
# Name: _Assertion_7_4_13(self, log)  Required Properties   - checked via json schema                                 
# Assertion text: 
# If an implementation supports a property, it shall always provide a value for that property.
# If a value is unknown, then null is an acceptable values in most cases. 
# required is True by default, so unless it is a False, it should be in the payload with a value or null
###################################################################################################
def Assertion_7_4_13(self, log):
    log.AssertionID = '7.4.13'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    annotation_term = 'required'

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = rf_utility.parse_odata_type(json_payload['@odata.type'])
                if namespace and typename:
                    json_metadata, schema_file = rf_utility.get_resource_json_metadata(namespace, self.json_directory)     
                    if json_metadata and schema_file:           
                        if verify_typename_in_json_metadata(typename, json_metadata):
                            if annotation_term in json_metadata['definitions'][typename]:
                                for req_prop in json_metadata['definitions'][typename][annotation_term]:                                       
                                    if req_prop not in json_payload.keys():
                                        assertion_status = log.FAIL
                                        log.assertion_log('line', "~ Resource: %s of type: %s has Annotation: '\%s'\ for property: %s in its schema document %s, but property not found in resource payload" % (json_payload['@odata.id'], namespace, annotation_term, req_prop, schema_file))                     
    log.assertion_log(assertion_status, None)
    return (assertion_status)

###################################################################################################
# check_property_in_payload()
#   This function check the payload for a non-nullable property
###################################################################################################
def check_property_in_payload(property, json_payload):
    for key in json_payload:
        if key == property.Name:
            #value cant be null
            if not json_payload[key]:
                return False
    return True

###################################################################################################
# Name: Assertion_7_4_14(self, log)  Required Properties  - checked via xml schema                                     
# Description: 
# Assertion text: required property should be annotated with Nullable = False
# cannot contain null values, (not necc to have the property in the payload?)
###################################################################################################
def Assertion_7_4_14(self, log):
    log.AssertionID = '7.4.14'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = csdl_schema_model.get_resource_namespace_typename(json_payload['@odata.type'])
                if namespace and typename:
                    #structural property
                    for property in typename.Properties:
                        if property.Nullable == 'false':
                            #check if the payload contains the key and its value
                            if not check_property_in_payload(property, json_payload):
                                assertion_status = log.FAIL
                                log.assertion_log('line', "Resource %s contains a Property: %s which has Annotation 'Nullable' set to 'false' but property's value is null in its resource urls payload %s" % (typename.Name, property.Name, relative_uris[relative_uri]))
                                
                    for navproperty in typename.NavigationProperties:
                        if navproperty.Nullable == 'false':
                            #check if the payload contains the key and its value
                            if not check_property_in_payload(navproperty, json_payload):
                                assertion_status = log.FAIL
                                log.assertion_log('line', "Resource %s contains a Navigation Property: %s which has Annotation 'Nullable' set to 'false' but property's value is null in its resource urls payload %s" % (typename.Name, property.Name, relative_uris[relative_uri]))
                                
    log.assertion_log(assertion_status, None)
    return (assertion_status)

###################################################################################################
# Name: Assertion_7_4_14(self, log)  Required Properties       - check via json schema                                
# Description: 
# Assertion text: required property should be annotated with Nullable = False
# cannot contain null values, (not necc to have the property in the payload?)
###################################################################################################
def _Assertion_7_4_14(self, log):
    log.AssertionID = '7.4.14'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    annotation_term = 'required'
    nullable_term = 'nullable'

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = rf_utility.parse_odata_type(json_payload['@odata.type'])
                if namespace and typename:
                    json_metadata, schema_file = rf_utility.get_resource_json_metadata(namespace, self.json_directory)     
                    if json_metadata and schema_file:           
                        if verify_typename_in_json_metadata(typename, json_metadata):
                            if annotation_term in json_metadata['definitions'][typename] and 'properties' in json_metadata['definitions'][typename]:
                                for req_prop in json_metadata['definitions'][typename][annotation_term]:                                       
                                    if req_prop in json_payload.keys():
                                        if nullable_term in json_metadata['definitions'][typename]['properties'][req_prop]:
                                            if not json_metadata['definitions'][typename]['properties'][req_prop][nullable_term]:
                                                if not json_payload[req_prop]:
                                                    assertion_status = log.FAIL
                                                    log.assertion_log('line', "~ Resource: %s of type: %s has Annotation: '\%s'\: %s for property: %s in its schema document %s, but value for property not found in resource payload" % (json_payload['@odata.id'], namespace, nullable_term, json_metadata['definitions'][typename]['properties'][req_prop][nullable_term], req_prop, schema_file))                     
    log.assertion_log(assertion_status, None)
    return (assertion_status)

###################################################################################################
# check_unit_instance(xtype, schema, namespace, log) WIP
# This helper function checks Redfish schema Annotation 'Measures.Unit' type. It should follow the 
# naming convention provided in ucum-essence.xml TODO parse ucum-essence to match the value 
###################################################################################################
def check_unit_instance(xtype, schema, namespace, log):
    if xtype.AttrKey:
        if xtype.AttrKey != 'String':
            assertion_status = log.FAIL
            log.assertion_log('line', "~ Property 'Measures.Unit': %s within Schema Namespace: %s in resource file %s is not of type string as required by the Redfish specification document %s" % (xtype.AttrKey, namespace.Namespace, schema.SchemaUri, REDFISH_SPEC_VERSION))   
        if xtype.AttrValue:
            if not isinstance(xtype.AttrValue, str):
                assertion_status = log.FAIL
                log.assertion_log('line', "~ The value of Property 'Measures.Unit': %s: %s within Schema Namespace: %s in resource file %s is not of type string as required by the Redfish specification document %s" % (xtype.AttrKey, xtype.AttrValue, namespace.Namespace, schema.SchemaUri, REDFISH_SPEC_VERSION))   
                     
###################################################################################################
# Name: Assertion_7_4_15(self, log) Units of Measure WIP                                  
# Assertion text: 
# In addition to following naming conventions, properties representing units of measure 
# shall be annotated with the Units annotation term in order to specify the units of measurement for 
# the property. check for annotation term 'Measures.Unit'
###################################################################################################
def Assertion_7_4_15(self, log):
    log.AssertionID = '7.4.15'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        #start with namespace
        for r_namespace in resource_namespaces:
            #check EntityType
            for entity_type in r_namespace.EntityTypes:
                unit = csdl_schema_model.get_annotation(entity_type, 'Measures.Unit')
                if unit:
                    check_unit_instance(unit, rf_schema, r_namespace, log)
                #check Property within EntityType
                for property in entity_type.Properties:
                    unit = csdl_schema_model.get_annotation(property, 'Measures.Unit')
                    if unit:
                        check_unit_instance(unit, rf_schema, r_namespace, log)
                #check NavigationProperty within EntityType
                for nav_property in entity_type.NavigationProperties:
                    unit = csdl_schema_model.get_annotation(nav_property, 'Measures.Unit')
                    if unit:
                        check_unit_instance(unit, rf_schema, r_namespace, log)

            #check ComplexType
            for complextype in r_namespace.ComplexTypes:
                unit = csdl_schema_model.get_annotation(complextype, 'Measures.Unit')
                if unit:
                    check_unit_instance(unit, rf_schema, r_namespace, log)
                #check Property within ComplexType
                for property in complextype.Properties:
                    unit = csdl_schema_model.get_annotation(property, 'Measures.Unit')
                    if unit:
                        check_unit_instance(unit, rf_schema, r_namespace, log)
                #check NavigationProperty within ComplexType
                for nav_property in complextype.NavigationProperties:
                    unit = csdl_schema_model.get_annotation(nav_property, 'Measures.Unit')
                    if unit:
                        check_unit_instance(unit, rf_schema, r_namespace, log)
                                                 
            #check Enumtype               
            for enum_type in r_namespace.EnumTypes:
                unit = csdl_schema_model.get_annotation(enum_type, 'Measures.Unit')
                if unit:
                    check_unit_instance(unit, rf_schema, r_namespace, log)
                #check Member within EnumType
                for member in enum_type.Members:
                    unit = csdl_schema_model.get_annotation(member, 'Measures.Unit')
                    if unit:
                        check_unit_instance(unit, rf_schema, r_namespace, log)

            #check Action       
            for action in r_namespace.Actions:
                unit = csdl_schema_model.get_annotation(action, 'Measures.Unit')
                if unit:
                    check_unit_instance(unit, rf_schema, r_namespace, log)


    log.assertion_log(assertion_status, None)
    return (assertion_status)
## end Assertion 7_4_15

###################################################################################################
# Name: Assertion_7_4_16(self, log) Reference Properties                                
# Assertion text: 
# All reference properties shall include Description and LongDescription annotations.
# NavigationProperty within EntityType and ComplexType
###################################################################################################
def Assertion_7_4_16(self, log):
    log.AssertionID = '7.4.16'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            entity_types = r_namespace.EntityTypes
            complextypes = r_namespace.ComplexTypes
            for entity_type in entity_types:
                for nav_prop in entity_type.NavigationProperties:
                    if not csdl_schema_model.verify_annotation_recur(nav_prop,'OData.Description'): 
                       assertion_status = log.FAIL
                       log.assertion_log('line', "~ NavigationProperty: %s, Type: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.Description' in its OData schema representation document: %s" % (nav_prop.Name, nav_prop.Type, rf_schema.SchemaUri))
                    if not csdl_schema_model.verify_annotation_recur(nav_prop,'OData.LongDescription'): 
                       assertion_status = log.FAIL
                       log.assertion_log('line', "~ NavigationProperty: %s, Type: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.LongDescription' in its OData schema representation document: %s" % (nav_prop.Name, nav_prop.Type, rf_schema.SchemaUri))   
            for complextype in complextypes:
                for nav_prop in complextype.NavigationProperties:
                    if not csdl_schema_model.verify_annotation_recur(nav_prop,'OData.Description'): 
                       assertion_status = log.FAIL
                       log.assertion_log('line', "~ NavigationProperty: %s, Type: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.Description' in its OData schema representation document: %s" % (nav_prop.Name, nav_prop.Type, rf_schema.SchemaUri))
                    if not csdl_schema_model.verify_annotation_recur(nav_prop,'OData.LongDescription'): 
                       assertion_status = log.FAIL
                       log.assertion_log('line', "~ NavigationProperty: %s, Type: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.LongDescription' in its OData schema representation document: %s" % (nav_prop.Name, nav_prop.Type, rf_schema.SchemaUri))   

    log.assertion_log(assertion_status, None)
    return (assertion_status)
## end Assertion 7_4_16

###################################################################################################
# Name: Assertion_7_4_18(self, log) Oem Property Format and Content   WIP                         
# Assertion text: 
# OEM-specified objects that are contained within the Oem property must be 
# valid JSON objects that follow the format of a Redfishcomplex type. 
###################################################################################################
def Assertion_7_4_18(self, log):
    log.AssertionID = '7.4.18'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            #look for Oem property, we have loaded it from json object so we already know its a json object
            if 'Oem' in json_payload:
                #find a property 
                #should follow complextype, should contain a dictionary and within that expect a key with dictionary as value
                # complextypes have properties and navigationproperties
                if not isinstance(json_payload['Oem'], dict):
                    assertion_status = log.FAIL
                    log.assertion_log('line',"~ Expected a dictionary as to satist complextype format which contains properties and navigational properties within the resource object " % (relative_uri, status) )
                else:
                    #this key is the name of the object, expected to have properties and navigational(reference) properties
                    for key in json_payload['Oem']:
                        if not isinstance(json_payload['Oem'][key], dict):
                            assertion_status = log.FAIL
                            log.assertion_log('line',"~ " % (relative_uri, status) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)

#end Assertion_7_4_18

###################################################################################################
# Name: Assertion_7_4_18_1(self, log) Oem Property Format and Content  WIP                            
# Assertion text: 
# OEM-specified objects... The name of the object (property) shall uniquely identify 
# the OEM or organization that manages the top of the namespace under which the property is defined.
###################################################################################################
def Assertion_7_4_18_1(self, log):
    log.AssertionID = '7.4.18.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            #look for Oem property, we have loaded it from json object so we already know its a json object
            if 'Oem' in json_payload:
                #find a property 
                #should follow complextype, should contain a dictionary and within that expect a key with dictionary as value
                # complextypes have properties and navigationproperties
                if not isinstance(json_payload['Oem'], dict):
                    assertion_status = log.FAIL
                    log.assertion_log('line',"~ " % (relative_uri, status) )
                else:
                    #this key is the name of the object so 1 key?, expected to have properties and navigational properties
                    for key in json_payload['Oem']:
                        if not isinstance(json_payload['Oem'][key], dict):
                            assertion_status = log.FAIL
                            log.assertion_log('line',"~ " % (relative_uri, status) )
                            
                        break

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#end Assertion_7_4_18_1

###################################################################################################
# Name: Assertion_7_4_18_2(self, log) Oem Property Format and Content WIP                             
# Assertion text: 
# The OEM-specified property shall also include a type property that provides
# the location of the schema and the type definition for the property within that schema. 
###################################################################################################
def Assertion_7_4_18_2(self, log):
    log.AssertionID = '7.4.18.2'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            #look for Oem property, we have loaded it from json object so we already know its a json object
            if 'Oem' in json_payload:
                #find a property 
                if not isinstance(json_payload['Oem'], dict):
                    assertion_status = log.FAIL
                    log.assertion_log('line',"~ " % (relative_uri, status) )
                else:
                    for key in json_payload['Oem']:
                        if not isinstance(json_payload['Oem'][key], dict):
                            assertion_status = log.FAIL
                            log.assertion_log('line',"~ " % (relative_uri, status) )
                        else:                            
                            if '@odata.type' not in json_payload['Oem'][key]:
                                assertion_status = log.FAIL
                                log.assertion_log('line',"~ " % (relative_uri, status) )

                            else: # contains namespace and typename
                                namespace, typename = csdl_schema_model.get_resource_namespace_typename(json_payload['Oem'][key]['@odata.type'])
                                if not namespace and not typename:
                                    assertion_status = log.FAIL
                                    log.assertion_log('line',"~ " % (relative_uri, status) )


    log.assertion_log(assertion_status, None)
    return (assertion_status)

#end Assertion_7_4_18_2

###################################################################################################
# check_name_instance(xtype, schema, log)
# This helper function checks Redfish schema property 'Name''s type. It should be a string 
###################################################################################################
def check_name_instance(xtype, schema, log):
    if xtype.Name:
        if not isinstance(xtype.Name, str):
            assertion_status = log.FAIL
            log.assertion_log('line', "~ Property 'Name': %s in resource file %s is not of type string as required by the Redfish specification document version: %s" % (xtype.Name, schema.SchemaUri, REDFISH_SPEC_VERSION))   

###################################################################################################
# Name: Assertion_7_5_1_2(self, log)  Description                                                
# Description: 
#
# Assertion text: 
#   The Name property is used to convey a human readable moniker for a resource.  The type of the Name 
#   property shall be string.  The value of Name is NOT required to be unique across resource instances
#   within a collection.
# checking EntityTypes under Schema
###################################################################################################
def Assertion_7_5_1_2(self, log):
    log.AssertionID = '7.5.1.2'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        #start with namespace
        for r_namespace in resource_namespaces:
            #check EntityType
            for entity_type in r_namespace.EntityTypes:
                check_name_instance(entity_type, rf_schema, log)
                #check Property within EntityType
                for property in entity_type.Properties:
                    check_name_instance(property, rf_schema, log)
                #check NavigationProperty within EntityType
                for nav_property in entity_type.NavigationProperties:
                    check_name_instance(nav_property, rf_schema, log)

            #check completype
            for complextype in r_namespace.ComplexTypes:
                check_name_instance(complextype, rf_schema, log)
                #check Property within ComplexType
                for property in complextype.Properties:
                   check_name_instance(property, rf_schema, log)
                #check NavigationProperty within ComplexType
                for nav_property in complextype.NavigationProperties:
                    check_name_instance(nav_property, rf_schema, log)

            #check Enumtype           
            for enum_type in r_namespace.EnumTypes:
                check_name_instance(enum_type, rf_schema, log)
                #check Member within EnumType
                for member in enum_type.Members:
                   check_name_instance(member, rf_schema, log)
                     
            #check Action
            for action in r_namespace.Actions:
               check_name_instance(action, rf_schema, log)
               #check parameter within Action
               for parameter in action.Parameters:
                    check_name_instance(parameter, rf_schema, log)

    log.assertion_log(assertion_status, None)
    return (assertion_status)
## end Assertion 7_5_1_2

###################################################################################################
# check_description_instance(xtype, schema, namespace, log)
#  This helper function just checked if annotaion term 'Description' has a property named 'String' 
#  and the value of this property should be a String type value aswell
###################################################################################################
def check_description_instance(xtype, schema, namespace, log):
    if xtype.AttrKey:
        if xtype.AttrKey != 'String':
            assertion_status = log.FAIL
            log.assertion_log('line', "~ Property 'Description': %s within Schema Namespace: %s in resource file %s is not of type string as required by the Redfish specification document %s" % (xtype.AttrKey, namespace.Namespace, schema.SchemaUri, REDFISH_SPEC_VERSION))   
        if xtype.AttrValue:
            if not isinstance(xtype.AttrValue, str):
                assertion_status = log.FAIL
                log.assertion_log('line', "~ The value of Property 'Description': %s: %s within Schema Namespace: %s in resource file %s is not of type string as required by the Redfish specification document %s" % (xtype.AttrKey, xtype.AttrValue, namespace.Namespace, schema.SchemaUri, REDFISH_SPEC_VERSION))   
                                              
###################################################################################################
# Name: Assertion_7_5_1_3(self, log)  Description                                                
# Assertion text: 
# The Description property is used to convey a human readable description of the resource. The type
# of the Description property shall be string. checking EntityTypes under Schema
###################################################################################################
def Assertion_7_5_1_3(self, log):
    log.AssertionID = '7.5.1.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        #start with namespace
        for r_namespace in resource_namespaces:
            #check EntityType
            for entity_type in r_namespace.EntityTypes:
                description = csdl_schema_model.get_annotation_recur(entity_type, 'OData.Description')
                if description:
                    check_description_instance(description, rf_schema, r_namespace, log)
                #check Property within EntityType
                for property in entity_type.Properties:
                    description = csdl_schema_model.get_annotation_recur(property, 'OData.Description')
                    if description:
                        check_description_instance(description, rf_schema, r_namespace, log)
                #check NavigationProperty within EntityType
                for nav_property in entity_type.NavigationProperties:
                    description = csdl_schema_model.get_annotation_recur(nav_property, 'OData.Description')
                    if description:
                        check_description_instance(description, rf_schema, r_namespace, log)

            #check ComplexType
            for complextype in r_namespace.ComplexTypes:
                description = csdl_schema_model.get_annotation_recur(complextype, 'OData.Description')
                if description:
                    check_description_instance(description, rf_schema, r_namespace, log)
                #check Property within ComplexType
                for property in complextype.Properties:
                    description = csdl_schema_model.get_annotation_recur(property, 'OData.Description')
                    if description:
                        check_description_instance(description, rf_schema, r_namespace, log)
                #check NavigationProperty within ComplexType
                for nav_property in complextype.NavigationProperties:
                    description = csdl_schema_model.get_annotation_recur(nav_property, 'OData.Description')
                    if description:
                        check_description_instance(description, rf_schema, r_namespace, log) 
                                                 
            #check Enumtype               
            for enum_type in r_namespace.EnumTypes:
                description = csdl_schema_model.get_annotation_recur(enum_type, 'OData.Description')
                if description:
                    check_description_instance(description, rf_schema, r_namespace, log)  
                #check Member within EnumType
                for member in enum_type.Members:
                    description = csdl_schema_model.get_annotation_recur(member, 'OData.Description')
                    if description:
                        check_description_instance(description, rf_schema, r_namespace, log) 

            #check Action       
            for action in r_namespace.Actions:
                description = csdl_schema_model.get_annotation_recur(action, 'OData.Description')
                if description:
                    check_description_instance(description, rf_schema, r_namespace, log)   


    log.assertion_log(assertion_status, None)
    return (assertion_status)
## end Assertion 7_5_1_3

###################################################################################################
# run(self, log):
# Takes sut obj and logger obj 
###################################################################################################
def run(self, log):
    #Section 7
    assertion_status = Assertion_7_0_1(self, log)
    assertion_status = Assertion_7_1_1(self, log)
    assertion_status = Assertion_7_4_3(self, log)
    assertion_status = Assertion_7_4_4(self, log)
    assertion_status = Assertion_7_4_6(self, log)
    assertion_status = Assertion_7_4_8(self, log)
    assertion_status = Assertion_7_4_9(self, log)
    assertion_status = Assertion_7_4_10(self, log)      
    assertion_status = Assertion_7_4_11(self, log)
    assertion_status = Assertion_7_4_13(self, log)        
    assertion_status = Assertion_7_4_14(self, log)
    assertion_status = Assertion_7_4_16(self, log)
    #WIP
    #assertion_status = Assertion_7_4_18(self, log)
    #WIP
    #assertion_status = Assertion_7_4_18_1(self, log)
    #WIP
    #assertion_status = Assertion_7_4_18_2(self, log)
    assertion_status = Assertion_7_5_1_2(self, log)
    assertion_status = Assertion_7_5_1_3(self, log)   
