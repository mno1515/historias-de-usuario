from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Producto, Categoria, Proveedor
from .forms import ProductoForm, CategoriaForm, FiltroInventarioForm, ProveedorForm


def inventario(request):
    form_filtro = FiltroInventarioForm(request.GET or None)
    form_modal_errors = False

    if request.method == "POST":
        accion = request.POST.get("accion", "")

        # ── PRODUCTO: crear ──
        if accion == "crear_producto":
            form = ProductoForm(request.POST)
            if form.is_valid():
                p = form.save()
                messages.success(request, f'Herramienta "{p.nombre}" creada correctamente.')
                return redirect("inventario:inventario")
            else:
                form_modal_errors = True

        # ── PRODUCTO: editar ──
        elif accion == "editar_producto":
            pk = request.POST.get("producto_id")
            producto = get_object_or_404(Producto, pk=pk)
            form = ProductoForm(request.POST, instance=producto)
            if form.is_valid():
                form.save()
                messages.success(request, f'Herramienta "{producto.nombre}" actualizada correctamente.')
                return redirect("inventario:inventario")
            else:
                messages.error(request, "Error al guardar. Revisa los campos.")

        # ── PRODUCTO: eliminar ──
        elif accion == "eliminar_producto":
            pk = request.POST.get("producto_id")
            producto = get_object_or_404(Producto, pk=pk)
            nombre = producto.nombre
            producto.delete()
            messages.success(request, f'Herramienta "{nombre}" eliminada.')
            return redirect("inventario:inventario")

        # ── CATEGORÍA: crear ──
        elif accion == "crear_categoria":
            nombre = request.POST.get("cat_nombre", "").strip()
            descripcion = request.POST.get("cat_descripcion", "").strip()
            if nombre:
                Categoria.objects.create(nombre=nombre, descripcion=descripcion or None)
                messages.success(request, f'Categoría "{nombre}" creada correctamente.')
            else:
                messages.error(request, "El nombre de la categoría es obligatorio.")
            return redirect("inventario:inventario")

        # ── CATEGORÍA: editar ──
        elif accion == "editar_categoria":
            pk = request.POST.get("categoria_id")
            categoria = get_object_or_404(Categoria, pk=pk)
            nombre = request.POST.get("cat_nombre", "").strip()
            descripcion = request.POST.get("cat_descripcion", "").strip()
            if nombre:
                categoria.nombre = nombre
                categoria.descripcion = descripcion or None
                categoria.save()
                messages.success(request, f'Categoría "{nombre}" actualizada.')
            else:
                messages.error(request, "El nombre de la categoría es obligatorio.")
            return redirect("inventario:inventario")

        # ── CATEGORÍA: eliminar ──
        elif accion == "eliminar_categoria":
            pk = request.POST.get("categoria_id")
            categoria = get_object_or_404(Categoria, pk=pk)
            nombre = categoria.nombre
            categoria.delete()
            messages.success(request, f'Categoría "{nombre}" eliminada.')
            return redirect("inventario:inventario")

        # ── PROVEEDOR: crear ──
        elif accion == "crear_proveedor":
            form_prov = ProveedorForm(request.POST)
            if form_prov.is_valid():
                p = form_prov.save()
                messages.success(request, f'Proveedor "{p.nombre}" creado correctamente.')
            else:
                messages.error(request, "Error al guardar el proveedor. Revisa los campos.")
            return redirect("inventario:inventario")

        # ── PROVEEDOR: editar ──
        elif accion == "editar_proveedor":
            pk = request.POST.get("proveedor_id")
            proveedor = get_object_or_404(Proveedor, pk=pk)
            form_prov = ProveedorForm(request.POST, instance=proveedor)
            if form_prov.is_valid():
                form_prov.save()
                messages.success(request, f'Proveedor "{proveedor.nombre}" actualizado.')
            else:
                messages.error(request, "Error al actualizar el proveedor.")
            return redirect("inventario:inventario")

        # ── PROVEEDOR: eliminar ──
        elif accion == "eliminar_proveedor":
            pk = request.POST.get("proveedor_id")
            proveedor = get_object_or_404(Proveedor, pk=pk)
            nombre = proveedor.nombre
            proveedor.delete()
            messages.success(request, f'Proveedor "{nombre}" eliminado.')
            return redirect("inventario:inventario")

    # ── GET: lista con filtros ──
    productos = Producto.objects.select_related("categoria", "proveedor").all()
    categorias = Categoria.objects.prefetch_related("productos").all()
    proveedores = Proveedor.objects.all()

    if form_filtro.is_valid():
        busqueda = form_filtro.cleaned_data.get("busqueda")
        categoria = form_filtro.cleaned_data.get("categoria")
        if busqueda:
            productos = productos.filter(
                Q(nombre__icontains=busqueda) | Q(codigo_sku__icontains=busqueda)
            )
        if categoria:
            productos = productos.filter(categoria=categoria)

    return render(request, "inventario.html", {
        "productos": productos,
        "categorias": categorias,
        "proveedores": proveedores,
        "form_filtro": form_filtro,
        "form_modal_errors": form_modal_errors,
        "total": productos.count(),
    })