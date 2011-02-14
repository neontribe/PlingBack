from plingback.idgen import FeedbackIdManager

def populate_id_pool(request):
    mgr = FeedbackIdManager(request.context)
    result = mgr.populate_id_pool()
    return result