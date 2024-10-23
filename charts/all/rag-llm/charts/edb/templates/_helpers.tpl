{{/*
Expand the name of the chart.
*/}}
{{- define "edb.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "edb.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "edb.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "edb.labels" -}}
helm.sh/chart: {{ include "edb.chart" . }}
{{ include "edb.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "edb.selectorLabels" -}}
app.kubernetes.io/name: {{ include "edb.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "edb.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "edb.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}


{{/*
Extracts everything after the slash and removes everything after the last dash.
Input example: value/value-value-02
Output: value-value
This is the required format for servingRuntime
*/}}
{{- define "extractModelId" -}}
  {{- $input := . -}}
  {{- $afterSlash := regexReplaceAll "^.*/" $input "" -}}
  {{- $beforeLastDash := regexReplaceAll "-[^-]*$" $afterSlash "" -}}
  {{- $beforeLastDash -}}
{{- end -}}