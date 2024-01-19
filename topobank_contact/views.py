from django.conf import settings
from django.shortcuts import reverse

from trackstats.models import Metric

from rest_framework.decorators import api_view
from rest_framework.response import Response

from topobank.usage_stats.utils import increase_statistics_by_date_and_object
from topobank.analysis.utils import filter_and_order_analyses
from topobank.analysis.controller import AnalysisController


@api_view(['GET'])
def contact_mechanics_card_view(request, **kwargs):
    controller = AnalysisController.from_request(request, **kwargs)

    #
    # for statistics, count views per function
    #
    increase_statistics_by_date_and_object(Metric.objects.ANALYSES_RESULTS_VIEW_COUNT, obj=controller.function)

    #
    # Trigger missing analyses
    #
    controller.trigger_missing_analyses()

    #
    # Basic context data
    #
    context = controller.get_context(request=request)

    #
    # Filter only successful ones
    #
    analyses_success = controller.get(['su'], True)

    if len(analyses_success) > 0:
        #
        # order analyses such that surface analyses are coming last (plotted on top)
        #
        analyses_success = filter_and_order_analyses(analyses_success)
        data_sources_dict = []

        #
        # Generate two plots in two tabs based on same data sources
        #
        for a_index, analysis in enumerate(analyses_success):
            subject_name = analysis.subject.name

            #
            # Context information for this data source
            #
            data_sources_dict += [{
                'sourceName': f'analysis-{analysis.id}',
                'subjectName': subject_name,
                'subjectNameIndex': a_index,
                'url': reverse('analysis:data', args=(analysis.pk, 'result.json')),
                'showSymbols': True,  # otherwise symbols do not appear in legend
                'width': 1.
            }]

        context['plotConfiguration'] = {
            'dataSources': data_sources_dict,
            'outputBackend': settings.BOKEH_OUTPUT_BACKEND
        }

    context['limitsToFunctionKwargs'] = settings.CONTACT_MECHANICS_KWARGS_LIMITS

    return Response(context)
