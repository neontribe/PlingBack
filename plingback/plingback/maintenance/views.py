from plingback.idgen import FeedbackIdManager

def populate_id_pool(request):
    mgr = FeedbackIdManager(request)
    result = mgr.populate_id_pool()
    return result