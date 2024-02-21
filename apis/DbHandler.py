import marqo
from UniqueDict import UniqueDict
from typing import List, Dict, Any, Union
import logging as log

# Run Marqo on m1 macs --> https://docs.marqo.ai/0.0.21/m1_mac_users/
class DbHandler():
    def __init__(self, config: UniqueDict):
        hostname = str(config.get("hostname"))
        port = str(config.get("port"))
        url = hostname + ":" + port
        self.mq = marqo.Client(url=url)
    
    def createIndex(self, indexName: str) -> Dict[str, Any]:
        # returns the following dict {'acknowledged': True, 'index': indexName}
        return self.mq.create_index(indexName)
    
    def createIndexIfNotExist(self, indexName:str) -> Dict[str, Any]:
        result = self.getAllIndexes()
        allIndexes = result['results']

        if len(allIndexes) == 0:
            return self.createIndex(indexName)
        
        for indexDict in allIndexes:
           if indexName == indexDict['indexName']:
                return {'index': indexName, 'acknowledged': True}
        
        return self.createIndex(indexName)

    def deleteIndex(self, indexName: str) -> Dict[str, Any]:
        """
            returns following dict
            {'acknowledged' : True}

            most likely an async operation
        """
        return self.mq.delete_index(indexName)
    
    def deleteAllIndexes(self) -> List[Dict[str, Any]]:
        log.warn("Deleting all indexes")
        response = []
        result = self.getAllIndexes()
        allIndexes = result['results']
        for indexDict in allIndexes: 
            indexName = indexDict['indexName']
            response.append(self.deleteIndex(indexName))
        return response
        
    def addDocuments(
        self, 
        indexName: str, 
        documents: List[dict], 
        tensorFields: List[str]
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        returns the following dict 
        {
          'errors': False,
          'processingTimeMs': 428.8912090005397,
          'index_name': 'myFirstIndex',
          'items': [{'status': 200, '_id': documentId}]
        }
        """

        return self.mq.index(indexName).add_documents(
            documents=documents,
            tensor_fields=tensorFields,
            client_batch_size=24
        )
    
    def addSingleDocument(
        self,
        indexName: str,
        document: dict, tensorFields: List[str]
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:

        return self.addDocuments(indexName, [document], tensorFields)

    def getStats(self, indexName: str) -> Any:
        return self.mq.index(indexName).get_stats()
    
    def searchInIndex(self, indexName: str, query:str, filter:str) -> Dict[str, Any]:
        """
        returns the following dict
        {
            "hits" : [
                {
                    '_id' : id of the doc,
                    '_highlights' : [
                        {
                            keyInDoc: text which was a good match
                        }
                    ],
                    '_score' : float how good the match is

                    also contains the keys and values in the doc itself
                }
            ]
        }
        """
        return self.mq.index(indexName).search(q=query, approximate=True)
    
    def getIndexStatus(self, indexName: str) -> None:
        # only supported for marqo cloud
        return self.mq.index(indexName).get_status()
    
    def getAllIndexes(self) -> Dict[str, str]:
        return self.mq.get_indexes()
    
    def deleteDocument(self, indexName:str, ids: List[str]) -> Dict[str, int]:
        """
            returns the following dict
            {
                'index_name': 'myFirstIndex',
                'status': 'succeeded',
                'type': 'documentDeletion',
                'items': [
                    {
                        '_id' : id of doc which was deleted,
                        'status' : status (should be 200 if okay),
                        'result' : should be 'deleted'
                    }
                ],
                'details': {
                    'receivedDocumentIds': 1,
                    'deletedDocuments': 1
                }, 
                'duration': 'PT0.060943S', 
                'startedAt': '2024-02-16T08:37:43.832820Z', 
                'finishedAt': '2024-02-16T08:37:43.893763Z'
            }
        """
        return self.mq.index(indexName).delete_documents(ids)
