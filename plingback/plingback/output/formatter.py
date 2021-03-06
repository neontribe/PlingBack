from statlib import stats

class ResultFormatter(object):
    """ Format the response from the plingbacks store """
    
    def __init__(self, data, sparql=None):
        self.data = data
        self.sparql = sparql

        
    def _format_ratings(self, output):
        ratings = []
        for result in self.data:
            try:
                ratings.append( float(result[0].toPython()) )
            except ValueError:
                pass
        output['results'] = {}
        if ratings:
            output['results']['median'] = stats.medianscore(ratings)
            output['results']['mode'] = stats.mode(ratings)
            output['results']['mean'] = stats.mean(ratings)
            output['results']['histogram'] = stats.histogram(ratings,6)
            output['results']['cumfreq'] = stats.cumfreq(ratings,6)
        output['results']['count'] = len(ratings)
        return output
    
    def _format_approvals(self, output):
        output['results'] = {'approvals':{}}
        for result in self.data:
            try:
                output['results']['approvals'][str(result[1])] = int(result[0].toPython())
            except ValueError:
                pass
        return output
    
    def _format_comments(self, output):
        comments = []
        for result in self.data:
            comments.append( {'text': str(result[0]),
                              'activity': str(result[1])} )
        output['results'] = {}
        if comments:
            output['results']['comments'] = comments
        output['results']['count'] = len(comments)
        return output
    
    def _format_scope(self, output):
        groups = {}
        total = 0
        for group in self.data:
            groups[str(group[0])] = int(group[1])
            total += int(group[1])
        output['results'] = groups
        output['totalFeedbackCount'] = total
        return output
        
    def _format_scope_and_id(self, output):
        groups = {}
        total = 0
        for group in self.data:
            groups['count'] = int(group[0])
            total += int(group[0])
        output['results'] = groups
        output['totalFeedbackCount'] = total
        return output
        
    def format(self):
        if not self.sparql:
            return self.data
        else:
            output = {}
            output['queryScope'] = self.sparql.scope
            output['id'] = self.sparql.id
            output['feedbackType'] = self.sparql.attribute
            if self.sparql.attribute:
                output = getattr(self, '_format_' + self.sparql.attribute)(output)
            elif self.sparql.scope and not self.sparql.id:
                output = self._format_scope(output)
            elif self.sparql.scope and self.sparql.id:
                output = self._format_scope_and_id(output)
                
            return output
                