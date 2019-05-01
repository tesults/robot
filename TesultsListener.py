import os.path
import sys
import tempfile
import configparser
import tesults

class TesultsListener:
    ROBOT_LISTENER_API_VERSION = 2

    data = {
    'target': 'token',
    'results': { 'cases': [] }
    }

    target = None
    config = None
    filespath = None
    buildName = None
    buildDesc = None
    buildResult = None
    buildReason = None
    disabled = False

    def filesForTest (self, suite, name):
        if (self.filespath is None):
            return
        files = []
        if (suite is None):
            suite = ''
        path = os.path.join(self.filespath, suite, name)
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for file in filenames:
                    if file != '.DS_Store': # Exclude os files
                        files.append(os.path.join(path, file))
        else:
            if (suite is not None):
                suiteSplit = suite.split(".")
                suiteSplit.insert(0, self.filespath)
                suiteSplit.append(name)
                path = os.path.join(*suiteSplit)
                if os.path.isdir(path):
                    for dirpath, dirnames, filenames in os.walk(path):
                        for file in filenames:
                            if file != '.DS_Store': # Exclude os files
                                files.append(os.path.join(path, file))
        return files

    def configFileExtraction (self):
        if (self.config is None):
            return
        configFileData = None
        try:
            configparse = configparser.ConfigParser()
            configparse.read(self.config)
            configFileData = configparse['tesults']
        except KeyError as error:
            print('KeyError in configuration file: ' + str(error))
        except ValueError as error:
            print('ValueError in configuration file: ' + str(error))
        except configparser.MissingSectionHeaderError as error:
            print('MissingSectionHeaderError in configuration file, check [tesults] is present: ' + str(error))
        
        try:
            if (configFileData):
                targetValue = configFileData[self.target]
                if (targetValue is not None):
                    self.target = targetValue
                if (self.filespath is None):
                    filespath = configFileData['files']
                    if (filespath is not None):
                        self.filespath = filespath
                if (self.buildName is None):
                    buildNameValue = configFileData['build-name']
                    if (buildNameValue is not None):
                        self.buildName = buildNameValue
                if (self.buildDesc is None):
                    buildDescValue = configFileData['build-desc']
                    if (buildDescValue is not None):
                        self.buildDesc = buildDescValue
                if (self.buildReason is None):
                    buildReasonValue = configFileData['build-reason']
                    if (buildReasonValue is not None):
                        self.buildReason = buildReasonValue
                if (self.buildResult is None):
                    buildResultValue = configFileData['build-result']
                    if (buildResultValue is not None):
                        self.buildResult = buildResultValue
        except ValueError as error:
            print('ValueError in configuration file: ' + str(error))
            raise error
        except KeyError as error:
            print('')


    # command: robot --listener PythonListener.py tests.robot
    def __init__(self, *argv):
        for arg in argv:
            if (arg.find("target=") != -1):
                self.target = arg[7 : len(arg)]
            if (arg.find("config=") != -1):
                self.config = arg[7 : len(arg)]
            if (arg.find("files=") != -1):
                self.filespath = arg[6 : len(arg)]
            if (arg.find("build-name=") != -1):
                self.buildName = arg[11 : len(arg)]
            if (arg.find("build-desc=") != -1):
                self.buildDesc = arg[11 : len(arg)]
            if (arg.find("build-result=") != -1):
                self.buildResult = arg[13 : len(arg)]
            if (arg.find("build-reason=") != -1):
                self.buildReason = arg[13 : len(arg)]
        if (self.target is None):
            self.disabled = True
            print("TesultsListener disabled. No target supplied.")
        else:
            self.configFileExtraction()
            

    def end_test(self, name, attributes):
        if (self.disabled == True):
            return
        testcase = {
            'name': name, 
        }
        suite = attributes.get('longname')
        suite = suite[0 : suite.rfind('.')]
        if (suite.find('Robot-Test.') == 0):
            suite = suite[11 : len(suite)]
        if (suite != ''):
            testcase['suite'] = suite
        
        desc = attributes.get('doc')
        if (desc is not None):
            testcase['desc'] = desc
        result = attributes.get('status')
        if (result is not None):
            if (result.lower() == 'pass'):
                testcase['result']= 'pass'
            elif (result.lower() == 'fail'):
                testcase['result'] = 'fail'
            else:
                testcase['result'] = 'unknown'
        reason = attributes.get('message')
        if (reason is not None):
            testcase['reason'] = reason
        duration = attributes.get('elapsedtime')
        if (duration is not None):
            duration = str(duration / 1000)
            start = attributes.get('starttime')
            if (start is None):
                start = ''
            end = attributes.get('endtime')
            if (end is None):
                end = ''
            testcase['_Time'] = duration + ' seconds ' + start + ' - ' + end
        tags = attributes.get('tags')
        if (tags is not None):
            if (len(tags) > 0):
                testcase['_Tags'] = str(tags)
        if (self.filespath != None):
            files = self.filesForTest(suite, name)
            if (files is not None):
                if (len(files) > 0):
                    testcase['files'] = files
        self.data['results']['cases'].append(testcase)

    def close(self):
        if (self.disabled == True):
            return
        if (self.buildName is not None):
            buildcase = {
                'name': self.buildName,
                'suite': '[build]',
                'result': 'unknown'
            }
            if (self.buildResult is not None):
                if (self.buildResult.lower() == 'pass'):
                    buildcase['result'] = 'pass'
                if (self.buildResult.lower() == 'fail'):
                    buildcase['result'] = 'fail'
            if (self.buildDesc is not None):
                buildcase['desc'] = self.buildDesc
            if (self.buildReason is not None):
                buildcase['reason'] = self.buildReason
            if (self.filespath is not None):
                files = self.filesForTest(buildcase['suite'], buildcase['name'])
                if (files is not None):
                    if (len(files) > 0):
                        buildcase['files'] = files
            self.data['results']['cases'].append(buildcase)
        
        self.data['target'] = self.target
        print('-----Tesults results upload...-----')
        if len(self.data['results']['cases']) > 0:
            #print('data: ' + str(self.data))
            ret = tesults.results(self.data)
            print('success: ' + str(ret['success']))
            print('message: ' + str(ret['message']))
            print('warnings: ' + str(ret['warnings']))
            print('errors: ' + str(ret['errors']))
        else:
            print('No test results.')
