{%- extends "full.tpl" -%}


{%- block html_head -%}
  <meta charset="utf-8" />
  <title>{{resources['metadata']['name']}}</title>

  <script src="/static/components/require/require.js"></script>
  <script src="/static/components/jquery/dist/jquery.min.js"></script>

  {% for css in resources.inlining.css -%}
      <style type="text/css">
      {{ css }}
      </style>
  {% endfor %}

  <style type="text/css">
  /* Overrides of notebook CSS for static HTML export */
  body {
    overflow: visible;
    padding: 8px;
  }

  div#notebook {
    overflow: visible;
    border-top: none;
  }

  @media print {
    div.cell {
      display: block;
      page-break-inside: avoid;
    }
    div.output_wrapper {
      display: block;
      page-break-inside: avoid;
    }
    div.output {
      display: block;
      page-break-inside: avoid;
    }
  }
  </style>

  <!-- Loading mathjax macro -->
  {{ mathjax() }}
{%- endblock html_head -%}


{% block body %}
  {# load polyfills #}
  {% include "browserpdf-polyfills.tpl" %}
  {{ super() }}
{% endblock body %}
