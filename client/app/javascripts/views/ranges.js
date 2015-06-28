define([
    'backbone',
    'backgrid',
    'collections',
    'text!templates/_ranges.html'
], function (Backbone, Backgrid, collections, template) {
    var columns = [
        {
            name: 'type',
            cell: 'string',
            editable: false
        },
        {
            name: 'min',
            cell: 'string',
            editable: false
        },
        {
            name: 'max',
            cell: 'string',
            editable: false
        }
    ]

    return Backbone.View.extend({
        initialize: function () {
            this.collection = new collections.RangeCollection

            this.grid = new Backgrid.Grid({
                columns: columns,
                collection: this.collection
            })
        },

        render: function () {
            this.$el.html(template)
            this.$('.view-table').append(this.grid.render().$el.addClass('table'))
            this.collection.fetch({reset: true})
        }
    })
})
