from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import TodoForm
from .models import Todo
# Create your views here.


def home(request):
	return render(request, 'todo_app/home.html')

def signupuser(request):
	if request.method == 'GET':
		return render(request, 'todo_app/signupuser.html', {'form':UserCreationForm()})
	else:
		#create new user
		if request.POST['password1'] == request.POST['password2']:
			try:
				user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
				user.save()
				login(request, user)
				return redirect('currenttodos')

			except IntegrityError:
				context = {
					'form':UserCreationForm(),
					'error' : 'That username has already been taken. Try something else',
				}
				return render(request, 'todo_app/signupuser.html', context)

		else:
			#password didn't match
			context = {
				'form':UserCreationForm(),
				'error' : 'Passwords did not match',
			}
			return render(request, 'todo_app/signupuser.html', context)


def loginuser(request):
	if request.method == 'GET':
		return render(request, 'todo_app/loginuser.html', {'form':AuthenticationForm()})
	else:
		user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
		if user is None:
			context = {
				'form':AuthenticationForm(),
				'error':'Username and password did not match',
			}
			return render(request, 'todo_app/loginuser.html', context)
		else:
			login(request, user)
			return redirect('currenttodos')


@login_required
def logoutuser(request):
	if request.method == 'POST':
		logout(request)
		return redirect('home')

@login_required
def createtodo(request):
	if request.method == 'GET':
		return render(request, 'todo_app/createtodo.html', {'form':TodoForm()})
	else:
		try:
			form = TodoForm(request.POST)
			newtodo = form.save(commit=False)
			newtodo.user = request.user
			newtodo.save()
			return redirect('currenttodos')
		except ValueError:
			context ={
				'form':TodoForm(),
				'error':'title is too big. Try again',
			}
			return render(request, 'todo_app/createtodo.html', context)

@login_required
def currenttodos(request):
	todos = Todo.objects.filter(user=request.user, timecompleted__isnull=True)
	return render(request, 'todo_app/currenttodos.html', {'todos':todos})

@login_required
def completedtodos(request):
	todos = Todo.objects.filter(user=request.user, timecompleted__isnull=False).order_by('-timecompleted')
	return render(request, 'todo_app/completedtodos.html', {'todos':todos})

@login_required
def viewtodo(request, todo_pk):
	todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
	if request.method == 'GET':
		form = TodoForm(instance=todo)
		return render(request, 'todo_app/viewtodo.html', {'todo':todo,'form':form})
	else:
		try:
			form = TodoForm(request.POST, instance=todo)
			form.save()
			return redirect('currenttodos')
		except ValueError:
			return render(request, 'todo_app/viewtodo.html', {'todo':todo,'form':form, 'error':'title is too big. Try again'})


@login_required
def completetodo(request, todo_pk):
	todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
	if request.method == 'POST':
		todo.timecompleted = timezone.now()
		todo.save()
		return redirect('currenttodos')

@login_required
def deletetodo(request, todo_pk):
	todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
	if request.method == 'POST':
		todo.delete()
		return redirect('currenttodos')