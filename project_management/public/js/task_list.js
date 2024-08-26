frappe.listview_settings['Task'] = {
    refresh: function (listview) {
        console.log(listview);
        if (listview.views_list.current_view === "Gantt") {
            listview.page.add_inner_button(__("Export Gantt PDF"), () => {
                const ganttChartSVG = document.querySelector('.gantt');

                if (ganttChartSVG) {
                    svgExport.downloadPdf(ganttChartSVG, "Gantt Export");
                }

            });
        }
    }
};
