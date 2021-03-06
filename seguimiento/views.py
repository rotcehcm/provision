# -*- encoding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from main.forms import preguntaForm
from django.core.mail import send_mail
from .models import NuevaPregunta, Size, Actualizacion
from django import forms
from provision import settings
from datetime import datetime
from django.utils import formats

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Login
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse

from django.utils import timezone

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from .forms import ExtraForm

# Create your views here.
# class SeguiIndex(View):
# 	def get(self,request):
# 		template='seguimiento/index.html'
# 		# context={}
# 		return render(request,template)

# class SeguiStatus(TemplateView):

class SeguiStatus(View): # _inicio e _inicio_filtro

	@method_decorator(permission_required("auth.adm", login_url='_home'))
	def get(self,request,filtro=None):
		hoy=datetime.now()
		preguntas=NuevaPregunta.objects.all().order_by('-pk')
		if filtro=="True":
			preguntas=preguntas.filter(cerrado=True)
		elif filtro=="False":
			preguntas=preguntas.filter(cerrado=False)
		elif filtro=="Hoy":
			preguntas=preguntas.filter(contacto=datetime.now())
			rojo=True
		context={"mensajes":preguntas,'hoy':hoy}
		template_name="seguimiento/clientes.html"
		return render(request,template_name,context)

class Revisar(View):
	@method_decorator(permission_required("auth.adm"),)
	def get(self,request,id):
		print ("entro al get")
		template_name="seguimiento/revisar.html"
		mensaje=get_object_or_404(NuevaPregunta,pk=id)
		comments=mensaje.comments.filter(active=True).order_by('-created')
		extras=mensaje.extras.all()
		form2=ExtraForm()
		context={
		"mensaje":mensaje,
		"comments":comments,
		'form2':form2,
		'extras':extras,
		}
		return render(request,template_name,context)
		
	def post(self,request,id):
		# print ("entro a editar")
		msj=get_object_or_404(NuevaPregunta,pk=id)
		msj.nombre=request.POST.get("nombre","")
		# print("el nombre",msj.nombre)
		msj.tel=request.POST.get("tel","")
		msj.mail=request.POST.get("mail","")
		# Formateamos la fecha
		fecha=request.POST.get("contacto","")
		msj.size=request.POST.get("size","")
		msj.plazo=request.POST.get("plazo","")
		msj.save()

		# Dato ExtraForm
		form=ExtraForm(request.POST)
		ex=form.save(commit=False)
		# print('el objeto: ',msj)
		ex.pregunta=msj
		ex.save()
		
		return HttpResponseRedirect(reverse('_revisar', args=(id,)))

class Revisado(View):
	def post(self,request,id):
		print("Entro")
		msj=get_object_or_404(NuevaPregunta,pk=id)
		# Guardamos el comentario primero
		comentario=Actualizacion()
		if request.POST.get('coment')!="":
			comentario.body=request.POST.get('coment','Sin Comentario')
			comentario.pregunta=msj
			comentario.save()
		# ahora el mensaje
		# msj.comments=request.POST.get("coment","")
		msj.cerrado=True
		contacto=request.POST.get("contacto","")
		fecha_llamada=request.POST.get("fecha_llamada","")
		# formateamos fecha
		if not contacto=="None":
			msj.contacto=formateaFecha(contacto)
		else:
			msj.contacto=None
		# guardamos
		msj.save()
		return redirect("_inicio")

class Borra(View):
	def get(self,request,id):
		# print("entro")
		msj=get_object_or_404(NuevaPregunta,pk=id)
		msj.delete()
		return redirect("_inicio")



		

class RecibeGracias(View):
	def get(self,request):
		template="main/gracias.html"
		return render(request,template)

	def post(self,request):
		form=preguntaForm(request.POST)
		if form.is_valid():
			# Aqui guardamos en la base de datos asi de facil
			pregunta=form.save()
			# Bajamos el mail del cliente
			cliente_mail=form.data["mail"]
			cliente_name=form.data["nombre"]
			cliente_tel=form.data["tel"]
			cliente_tam=form.data["size"]
			cliente_plazo=form.data["plazo"]
			mensaje='Nueva Cotizacion DESDE PROVISION. http://www.pro-vision.com.mx/seguimiento/inicio/\n'
			mensaje+='Nombre: '+str(cliente_name)
			mensaje+='\nTelefono: '+str(cliente_tel)
			mensaje+='\nCorreo: '+str(cliente_mail)
			mensaje+='\nTamaño: '+str(cliente_tam)
			mensaje+='\nPlazo: '+str(cliente_plazo)
			# Notificamos a miguel
			try:
				send_mail(
					'Sistema Terrenos',
					mensaje,
					'sistema@fixter.org',
					['tterrenofacil@gmail.com'], fail_silently=False
					)
				# agradecemos al cliente y enviamos info
				send_mail(
					'Gracias por tu interez!',
					'Pronto te haremos una llamada.',
					'tterrenofacil@gmail.org',
					[cliente_mail], fail_silently=False
					)
			except:
				pass
			return redirect('_recibe')

			

		else:
			template_name="main/index.html"
			context={
			"form":form
			}
			return render(request,template_name,context)
class TakeForm(View):
	def get(self,request):
		template="main/gracias.html"
		return render(request,template)

	def post(self,request):
		nombre=request.POST.get("name","")
		nombre+=" - PVision"
		telefono=request.POST.get("tel","")
		mail=request.POST.get("mail","")
		size=request.POST.get("size","")
		plazo=request.POST.get("plazo")

		newPregunta=NuevaPregunta(
			nombre=nombre,
			tel=telefono,
			mail=mail,
			size=size,
			plazo=plazo,
			)
		newPregunta.save()
	# Notificamos a miguel
	# Con Plantilla:
		datos={
		'p':newPregunta
		}
		try:
			email_miguel(datos)


	# Sin Plantilla:
		# mensaje='Miguel, Tienes una nueva cotización pendiente DESDE PROVISION. http://www.pro-vision.com.mx/seguimiento/inicio/\n'
		# mensaje+='Nombre: '+nombre.encode("utf-8")
		# mensaje+='\nTelefono: '+str(telefono)
		# mensaje+='\nCorreo: '+str(mail)
		# mensaje+='\nTamaño: '+str(size)
		# mensaje+='\nPlazo: '+str(plazo)
		# send_mail(
		# 	'Sistema Terrenos',
		# 	mensaje,
		# 	'sistema@fixter.org',
		# 	['tterrenofacil@gmail.com'], fail_silently=False
		# 	)	
	# agradecemos al cliente y enviamos info
			send_mail(
				'Gracias por tu interez!',
				'Pronto te haremos una llamada.',
				'tterrenofacil@gmail.org',
				[mail], fail_silently=False
				)
		except:
			pass
		return redirect('_daform')


class Login(View):
	def get(self,request):
		template="seguimiento/login.html"
		if request.user.is_authenticated():
			return redirect("_inicio")
		else:
			# mensaje=""
			return render(request,template)


class TerrenoFacilForm(View):

	def get(self,request):
		nombre=request.GET.get("nombre","")
		nombre+=" - TFacil"
		telefono=request.GET.get("tel","")
		mail=request.GET.get("mail","")
		size=request.GET.get("size","")
		plazo=request.GET.get("plazo")

		newPregunta=NuevaPregunta(
			nombre=nombre,
			tel=telefono,
			mail=mail,
			size=size,
			plazo=plazo,
			)
		newPregunta.save()
	# Notificamos a miguel
	# con plantilla:
		datos={
		'p':newPregunta
		}
		try:
			email_miguel(datos)

	# sin plantilla:
		# mensaje='Miguel, Tienes una nueva cotización pendiente DESDE TERRENOFACIL http://www.pro-vision.com.mx/seguimiento/inicio/\n'
		# mensaje+='Nombre: '+str(nombre)
		# mensaje+='\nTelefono: '+str(telefono)
		# mensaje+='\nCorreo: '+str(mail)
		# mensaje+='\nTamaño: '+str(size)
		# mensaje+='\nPlazo: '+str(plazo)

		# send_mail(
		# 	'Sistema Terrenos',
		# 	mensaje,
		# 	'hola@fixter.org',
		# 	['tterrenofacil@gmail.com'], fail_silently=False
		# 	)
	# agradecemos al cliente y enviamos info
			send_mail(
				'Gracias por tu interez!',
				'Pronto te haremos una llamada.',
				'tterrenofacil@gmail.org',
				[mail], fail_silently=False
				)
		except:
			pass
		return redirect("http://www.terrenofacil.com.mx/gracias.html")

def formateaFecha(fecha):
	try:
		formateada = datetime.strptime(fecha, '%d %B, %Y')
	except:
		formateada=datetime.strptime(fecha,'%b. %d, %Y')
	return formateada

from django.template import Context
from django.template.loader import get_template
from django.core.mail import EmailMessage

def email_miguel(datos):
	subject="Nuevo Cliente"
	to=['tterrenofacil@gmail.com']
	from_email='tterrenofacil@gmail.com'
	ctx=datos

	message=get_template("seguimiento/email/nuevo.html").render(Context(ctx))
	msg=EmailMessage(subject,message,to=to,from_email=from_email)
	msg.content_subtype='html'
	msg.send()

# Envio de plantillas en nCorreo






