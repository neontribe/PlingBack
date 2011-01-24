from plingback.augmentations import ActivityAugmenter

def add_activity_nodes(request):
    aa = ActivityAugmenter(request)
    result = aa.add_activity_nodes()
    return result

def add_activity_data(request):
    aa = ActivityAugmenter(request)
    result = aa.add_activity_data()
    return result