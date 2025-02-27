from django.contrib import admin
from .models import Project, Sample, ResearchStandard, Report, ReportResearchStandard


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'assign_to', 'status', 'end_date')
    list_filter = ('status',)
    search_fields = ('name', 'client__email', 'assign_to__email')
    raw_id_fields = ('client', 'assign_to')  # Przydatne przy dużej liczbie użytkowników

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client', 'assign_to')


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('name', 'material_type_display', 'collection_date', 'short_description')
    list_filter = ('material_type',)
    search_fields = ('name', 'description')

    def material_type_display(self, obj):
        return obj.get_material_type_display()

    material_type_display.short_description = 'Rodzaj materiału'

    def short_description(self, obj):
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description # django nie pozwala dodawać pól typu many-to-many

    short_description.short_description = 'Opis'


@admin.register(ResearchStandard)
class ResearchStandardAdmin(admin.ModelAdmin):
    list_display = ('name', 'method')
    search_fields = ('name', 'method')


class ReportResearchStandardInline(admin.TabularInline):
    model = ReportResearchStandard
    extra = 1
    autocomplete_fields = ('research_standard',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('code_name', 'start_date', 'end_date', 'approved_by')
    list_filter = ('start_date', 'end_date')
    search_fields = ('code_name', 'project__name')
    raw_id_fields = ('project', 'sample', 'approved_by')
    inlines = (ReportResearchStandardInline,)



    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project', 'sample', 'approved_by')
