#!/usr/bin/env python
import boto.sqs
import yaml
from helper2 import Helper

class Sqs:
    
    def __init__(self, boto_sqs_connection, queue_name):
        self.queue = queue_name # string
        self.conn = boto_sqs_connection # live connection

    def get_queue_length(self):
        try:
            myq = self.conn.get_queue(self.queue)
        except:
            raise
        return  myq.count()
  
    def get_a_message(self):
        '''If we have at least one message in the queue, return it.
           Otherwise, return None''' 
        message = None
        try:
            myq = self.conn.get_queue(self.queue)
            q_length = myq.count()
            if q_length > 0:
                message = myq.read()
        except:
            raise
        return message

    def get_message_body(self, message):
        try:
            body = message.get_body()
        except Exception, e:
            raise
        return body

    def delete_a_message(self, message):
        try:
            myq = self.conn.get_queue(self.queue)
            myq.delete_message(message)
        except:
            raise
        return 


if __name__ == "__main__":
    h = Helper()
    region = h.get_region()
    queue_name = h.get_minion_queue_name()


    conn = boto.sqs.connect_to_region(region)
    s = Sqs(conn, queue_name)
    m = s.get_a_message()
    print m.__dict__
