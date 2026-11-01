"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Eye, EyeOff, Truck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuthStore } from "@/store/auth";

const loginSchema = z.object({
  email: z.string().email("Email invalide"),
  password: z.string().min(1, "Mot de passe requis"),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setError(null);
    try {
      await login(data.email, data.password);
      router.push("/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur de connexion");
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left — Image */}
      <div className="hidden lg:flex lg:w-1/2 bg-primary relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary via-primary-light/30 to-primary" />
        <div className="relative z-10 flex flex-col justify-between p-12 text-white">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-accent flex items-center justify-center">
              <Truck className="w-5 h-5 text-white" />
            </div>
            <span className="font-display font-bold text-xl">
              MMS<span className="text-accent-light">Express</span>
            </span>
          </div>
          <div className="max-w-md">
            <h2 className="font-display font-bold text-3xl mb-4 leading-tight">
              Pilotez vos livraisons en toute intelligence
            </h2>
            <p className="text-gray-300 leading-relaxed">
              Attribution automatique, suivi temps reel, analytics avances.
              Tout ce dont votre equipe a besoin pour livrer plus vite et mieux.
            </p>
          </div>
          <p className="text-sm text-gray-400">
            &copy; {new Date().getFullYear()} MMS Express
          </p>
        </div>
      </div>

      {/* Right — Form */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-12 bg-bg dark:bg-bg-dark">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-2 mb-10">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <Truck className="w-4 h-4 text-white" />
            </div>
            <span className="font-display font-bold text-lg text-primary dark:text-white">
              MMS<span className="text-accent">Express</span>
            </span>
          </div>

          <h1 className="font-display font-bold text-2xl sm:text-3xl text-gray-900 dark:text-white mb-2">
            Connexion
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mb-8">
            Entrez vos identifiants pour acceder a la plateforme
          </p>

          {error && (
            <div className="bg-error-light dark:bg-error/10 text-error text-sm font-medium px-4 py-3 rounded-[10px] mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <Input
              label="Email"
              type="email"
              placeholder="vous@entreprise.com"
              error={errors.email?.message}
              {...register("email")}
            />

            <div className="relative">
              <Input
                label="Mot de passe"
                type={showPassword ? "text" : "password"}
                placeholder="Votre mot de passe"
                error={errors.password?.message}
                {...register("password")}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-[38px] text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                tabIndex={-1}
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="rounded border-gray-300" />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Se souvenir de moi
                </span>
              </label>
              <Link
                href="/forgot-password"
                className="text-sm font-medium text-accent hover:text-accent-dark transition-colors"
              >
                Mot de passe oublie ?
              </Link>
            </div>

            <Button
              type="submit"
              isLoading={isSubmitting}
              className="w-full"
              size="lg"
            >
              Se connecter
            </Button>
          </form>

          <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-8">
            Pas encore de compte ?{" "}
            <Link
              href="/register"
              className="font-medium text-accent hover:text-accent-dark transition-colors"
            >
              Creer un compte
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
