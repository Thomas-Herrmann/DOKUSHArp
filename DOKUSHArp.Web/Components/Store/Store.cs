using Microsoft.AspNetCore.Components;
using System.Collections.Concurrent;
using System.Reflection;

namespace DOKUSHArp.Web.Components.Store;

public sealed class Store
{
	private readonly ConcurrentDictionary<Type, dynamic> stateMapping = [];
	private readonly ConcurrentDictionary<Type, SynchronizedCollection<StatefulComponent>> dependencyMapping = [];

	public async Task UpdateStateAsync<TState>(Func<TState, TState> updateFunc) where TState : class, IState<TState>
	{
		stateMapping.AddOrUpdate(typeof(TState), _ => updateFunc(TState.Default), (_, state) => updateFunc(state));

		if (!dependencyMapping.TryGetValue(typeof(TState), out var dependencyBag)) return;

		await Task.WhenAll(dependencyBag.Select(component => component.TriggerUpdateAsync())).ConfigureAwait(false);
	}

	public TState GetState<TState>() where TState : class, IState<TState> => stateMapping.GetOrAdd(typeof(TState), _ => TState.Default);

	public void RegisterForUpdates(StatefulComponent component)
	{
		foreach (var dependencyType in ExtractStateDependencyTypes(component))
			dependencyMapping.GetOrAdd(dependencyType, _ => []).Add(component);
	}

	public void DeregisterForUpdates(StatefulComponent component) 
	{
		foreach (var dependencyType in ExtractStateDependencyTypes(component))
			dependencyMapping.GetValueOrDefault(dependencyType)?.Remove(component);
	}

	private static IEnumerable<Type> ExtractStateDependencyTypes(StatefulComponent component) => component
		.GetType()
		.GetProperties(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance)
		.Where(info => info.PropertyType.IsGenericType && info.PropertyType.GetGenericTypeDefinition() == typeof(State<>) && Attribute.IsDefined(info, typeof(InjectAttribute)))
		.Select(info => info.PropertyType.GetGenericArguments()[0])
		.Distinct();
}