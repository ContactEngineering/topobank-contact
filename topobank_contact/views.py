import itertools

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import reverse

from trackstats.models import Metric

from rest_framework.decorators import api_view
from rest_framework.response import Response

from topobank.manager.models import Topography
from topobank.analysis.models import AnalysisFunction
from topobank.usage_stats.utils import increase_statistics_by_date_and_object
from topobank.analysis.utils import AnalysisController, round_to_significant_digits, filter_and_order_analyses, \
    palette_for_topographies


@api_view(['POST'])
def contact_mechanics_card_view(request):
    controller = AnalysisController.from_request(request)

    print(f'{len(controller())} analyses existed.')

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

    print(controller.unique_kwargs)

    #
    # Filter only successful ones
    #
    analyses_success = controller(['su'], True)

    if len(analyses_success) > 0:

        data_sources_dict = []

        analyses_success = filter_and_order_analyses(analyses_success)

        #
        # Prepare colors to be used for different analyses
        #
        color_cycle = itertools.cycle(palette_for_topographies(len(analyses_success)))

        #
        # Generate two plots in two tabs based on same data sources
        #
        for a_index, analysis in enumerate(analyses_success):
            curr_color = next(color_cycle)

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
                'color': curr_color,
                'width': 1.
            }]

        context['plotConfiguration'] = {
            'dataSources': data_sources_dict,
            'outputBackend': settings.BOKEH_OUTPUT_BACKEND
        }

    #
    # Calculate initial values for the parameter form on the page
    # We only handle topographies here so far, so we only take into account
    # parameters for topography analyses
    #
    topography_ct = ContentType.objects.get_for_model(Topography)
    try:
        unique_kwargs = context['uniqueKwargs'][topography_ct]
    except KeyError:
        unique_kwargs = None
    if unique_kwargs:
        initial_calc_kwargs = unique_kwargs
    else:
        # default initial arguments for form if we don't have unique common arguments
        contact_mechanics_func = AnalysisFunction.objects.get(name="Contact mechanics")
        initial_calc_kwargs = contact_mechanics_func.get_default_kwargs(topography_ct)
        initial_calc_kwargs['substrate_str'] = 'nonperiodic'  # because most topographies are non-periodic

    context['initialCalcKwargs'] = initial_calc_kwargs

    # context['extraWarnings'] = alerts
    context['extraWarnings'] = {
        'alertClass': 'alert-warning',
        'message': """
             Translucent data points did not converge within iteration limit and may carry large errors.
             <i>A</i> is the true contact area and <i>A0</i> the apparent contact area,
             i.e. the size of the provided measurement.
             """
    }

    context['limitsCalcKwargs'] = settings.CONTACT_MECHANICS_KWARGS_LIMITS

    context['api'] = {
        'submitUrl': reverse('analysis:card-submit')
    }

    return Response(context)
