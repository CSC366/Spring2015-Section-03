// The majority of this code is directly drawn from the React documentation.
React.initializeTouchEvents(true);
var converter = new Showdown.converter();
var QuestionViewer = React.createClass({
   loadCommentsFromServer: function() {
      $.ajax({
         url: this.props.url,
         dataType: 'json',
         success: function(data) {
            this.setState({data: data});
         }.bind(this),
         error: function(xhr, status, err) {
            console.error(this.props.url, status, err.toString());
         }.bind(this)
      });
   },
   getInitialState: function() {
      return {data: [], searchText: '', filters: {active: {}, enabled: false, negated: false}};
   },
   componentDidMount: function() {
      this.loadCommentsFromServer();
      setInterval(this.loadCommentsFromServer, this.props.pollInterval);
   },
   updateFilters: function(filters) {
      this.setState({filters: filters});
   },
   updateSearch: function(text) {
      this.setState({searchText: text});
   },
   render: function() {
      return (
         <div>
            <h2>Questions</h2>
            <div className="col-sm-3">
               <QuestionSearch search={this.state.searchText} onUpdate={this.updateSearch} />
               <QuestionFilter data={this.state.data} onUpdate={this.updateFilters} />
            </div>
            <div className="col-sm-9">
               <QuestionList data={this.state.data} search={this.state.searchText} filters={this.state.filters} />
            </div>
         </div>
      );
   }
});

var QuestionSearch = React.createClass({
   update: function() {
      this.props.onUpdate(
         this.refs.searchInput.getDOMNode().value
      );
   },
   render: function() {
      return (
         <form style={{"marginBottom": "10px"}}>
            <input type="text" ref="searchInput" placeholder="Filter..." value={this.props.search} onChange={this.update} />
         </form>
      );
   }
});

var QuestionFilter = React.createClass({
   updateFilter: function() {
      var filters = $(this.refs.filters.getDOMNode());
      var checkbox = $(this.refs.negate.getDOMNode());

      var anySet = false;
      var checkedKeys = {};
      filters.find('input').each(function() {
         var checkbox = $(this);
         if (checkbox.prop('checked')) {
            checkedKeys[checkbox.val()] = true;
            anySet = true;
         }
      });

      var negated = checkbox.prop('checked');

      this.props.onUpdate({active: checkedKeys, negated: negated, enabled: anySet});
   },
   render: function() {
      var keys = {};
      this.props.data.forEach(function (comment) {
         comment.keys.forEach(function (key) {
            keys[key] = true;
         });
      });

      var keywords = Object.keys(keys).map(function (key) {
         return (
            <div key={key} className="checkbox">
               <label>
                  <input onChange={this.updateFilter} value={key} type="checkbox" /> {key}
               </label>
            </div>
         );
      }, this);
      return (
         <form style={{"marginBottom": "10px"}}>
            <div ref="filters" className="form-group">
               {keywords}
            </div>
            <div className="form-group">
               <div className="checkbox">
                  <label>
                     <input ref="negate" type="checkbox" onChange={this.updateFilter} />
                     Reverse filter effect
                  </label>
               </div>
            </div>
         </form>
      );
   }
});

var QuestionList = React.createClass({
   render: function() {
      var search = new RegExp(this.props.search);
      var filters = this.props.filters;
      var commentNodes = this.props.data.filter(function (comment) {
         if (search.source) {
            return search.test(comment.Q) || search.test(comment.A);
         } else {
            return true;
         }
      }).filter(function (comment) {
         if (filters.enabled) {
            var any = false;
            comment.keys.forEach(function (key) {
               if (filters.active[key]) {
                  any = true;
               }
            });

            return any ^ filters.negated;
         } else {
            if (filters.negated) {
               return comment.keys.length === 0;
            }else {
               return true;
            }
         }
      }).map(function (comment) {
         return (
            <Question comment={comment}>
            </Question>
         );
      });
      return (
         <ul className="list-group">
            {commentNodes}
         </ul>
      );
   }
});

var Question = React.createClass({
   render: function() {
      return (
         <li className="list-group-item">
            <h3 className="commentAuthor">
               {this.props.comment.Q}
            </h3>
            <p>
            {this.props.comment.A}
            </p>
            <div>
            Keys: {this.props.comment.keys.join(', ')}
            </div>
         </li>
      );
   }
});

$(function() {
   React.render(
      <QuestionViewer url="data.json" pollInterval={2000} />,
      document.getElementById('content')
   );
})
