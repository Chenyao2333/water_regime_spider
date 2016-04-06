import csv
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse

from .models import Site, WaterFlow, WaterLevel


def to_datetime(ts):
    if ts:
        import datetime
        return datetime.datetime.fromtimestamp(float(ts))
    else:
        return None

def site_list(request):
    sites = Site.objects.filter(deleted=False)
    return render(request, "demon/site_list.html", {"sites": sites, "ts": 123})

def get_site_or_404(site_id):
    site = get_object_or_404(Site, pk=site_id)
    if site.deleted:
        raise Http404
    return site

def get_site_data_points(site_id):
    """Return a list formed by data points.
    [[date_0, flow_0, level_0], [date_1, flow_1, level_1]]
    """
    flow_points = WaterFlow.objects.filter(sid=site_id)
    level_points = WaterLevel.objects.filter(sid=site_id)

    data_points = {}
    for p in flow_points:
        t = p.date
        if t in data_points:
            data_points[t][0] = p.flow
        else:
            data_points[t] = [p.flow, None]
    for p in level_points:
        t = p.date
        if t in data_points:
            data_points[t][1] = p.level
        else:
            data_points[t] = [None, p.level]

    points = [[key,] + data_points[key] for key in sorted(data_points, reverse=True)]
    return points


def site_data(request, site_id):
    site = get_site_or_404(site_id)
    points = get_site_data_points(site_id)
    return render(request, "demon/site_data.html", {"site": site, "points": points})

def export_csv(request, site_id):
    site = get_site_or_404(site_id)
    points = get_site_data_points(site_id)
    
    response = HttpResponse(content_type="text/csv")

    writer = csv.writer(response)
    writer.writerow(["date", "flow", "level"])
    for p in points:
        p[0] = to_datetime(p[0])
        writer.writerow(p)

    return response

